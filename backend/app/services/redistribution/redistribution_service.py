from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import (
    DispatchStatusEnum,
    EmergencyStatusEnum,
    SeverityEnum,
    TransferStatusEnum,
    UserRoleEnum,
)
from app.models.dispatch import TransferDispatch
from app.models.emergency import EmergencyCase
from app.models.facility import Facility
from app.models.medicine import Medicine
from app.models.facility_user import FacilityUser
from app.models.inventory import InventoryBatch, InventoryCurrent
from app.models.transfer_batch_allocation import TransferBatchAllocation
from app.models.emergency_timeline_event import EmergencyTimelineEvent
from app.models.redistribution import TransferRequest
from app.services.emergency.matching_service import MatchingService
from app.services.inventory.shortage_service import ShortageService
from app.engines.inventory.medicine_safety import (
    plan_fefo_reservation,
    safe_transferable_quantity,
)
from app.services.redistribution.state_machine import validate_transfer_transition


class RedistributionService:
    """Transactional supply-request, approval, dispatch, and settlement workflow."""

    def __init__(self, db: Session):
        self.db = db
        self.matching_service = MatchingService(db)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def _record_timeline_event(
        self,
        emergency_case_id,
        transfer_id,
        actor_user_id,
        event_type: str,
        title: str,
        detail: str,
        payload: dict | None = None,
        occurred_at: datetime | None = None,
    ) -> None:
        """Append an operational event to the same transaction as its state change."""
        if emergency_case_id is None:
            return
        self.db.add(
            EmergencyTimelineEvent(
                emergency_case_id=emergency_case_id,
                transfer_id=transfer_id,
                actor_user_id=actor_user_id,
                event_type=event_type,
                title=title,
                detail=detail,
                event_payload=payload or {},
                occurred_at=occurred_at or self._now(),
            )
        )

    def _require_hospital_membership(self, user, facility_id: UUID) -> None:
        if user.role in {UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR}:
            return
        if user.role != UserRoleEnum.HOSPITAL_ADMIN:
            raise PermissionError("This role cannot perform hospital transfer decisions.")

        membership = self.db.execute(
            select(FacilityUser.facility_user_id).where(
                FacilityUser.user_id == user.user_id,
                FacilityUser.facility_id == facility_id,
                FacilityUser.assigned_role == UserRoleEnum.HOSPITAL_ADMIN,
            )
        ).scalar_one_or_none()
        if membership is None:
            raise PermissionError("Hospital administrator is not assigned to the destination facility.")

    def _require_operations_role(self, user) -> None:
        if user.role not in {UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR}:
            raise PermissionError("Only emergency operations or system administrators can manage dispatch.")

    @staticmethod
    def _serialize_transfer(transfer: TransferRequest) -> dict:
        return {
            "transfer_id": transfer.transfer_id,
            "emergency_case_id": transfer.emergency_case_id,
            "from_facility_id": transfer.from_facility_id,
            "from_facility_name": transfer.source_facility.facility_name,
            "to_facility_id": transfer.to_facility_id,
            "to_facility_name": transfer.destination_facility.facility_name,
            "medicine_id": transfer.medicine_id,
            "medicine_name": transfer.medicine.medicine_name,
            "requested_quantity": transfer.requested_quantity,
            "approved_quantity": transfer.approved_quantity,
            "transfer_status": transfer.transfer_status,
            "cascade_safe": transfer.cascade_safe,
            "match_score": float(transfer.match_score) if transfer.match_score is not None else None,
            "transfer_distance_km": float(transfer.transfer_distance_km) if transfer.transfer_distance_km is not None else None,
            "recommendation_reason": transfer.recommendation_reason,
            "requested_at": transfer.requested_at,
            "completed_at": transfer.completed_at,
        }

    def request_transfer_from_emergency(self, emergency_case_id: UUID, user) -> dict:
        """Create one pending transfer leg per ranked donor until demand is covered.

        This records requests only. It does not reserve or move stock until a
        destination Hospital Admin approves each leg.
        """
        try:
            emergency = self.db.execute(
                select(EmergencyCase)
                .where(EmergencyCase.emergency_case_id == emergency_case_id)
                .with_for_update()
            ).scalar_one_or_none()
            if emergency is None:
                raise LookupError("Emergency case not found.")

            self._require_hospital_membership(user, emergency.facility_id)

            active_statuses = [
                TransferStatusEnum.PENDING,
                TransferStatusEnum.APPROVED,
                TransferStatusEnum.IN_TRANSIT,
            ]
            existing = self.db.execute(
                select(TransferRequest)
                .where(
                    TransferRequest.emergency_case_id == emergency_case_id,
                    TransferRequest.transfer_status.in_(active_statuses),
                )
                .order_by(TransferRequest.requested_at.asc())
                .with_for_update()
            ).scalars().all()
            if existing:
                self.db.commit()
                return {
                    "emergency_case_id": emergency_case_id,
                    "transfer_ids": [row.transfer_id for row in existing],
                    "recommended_quantity": sum(row.requested_quantity for row in existing),
                    "unfilled_quantity": max(
                        0,
                        (emergency.required_quantity or 0)
                        - (emergency.available_quantity or 0)
                        - sum(row.requested_quantity for row in existing),
                    ),
                    "donor_count": len(existing),
                    "idempotent_replay": True,
                    "message": "Existing transfer requests returned; no duplicate requests were created.",
                }

            if emergency.emergency_status in {
                EmergencyStatusEnum.RESOLVED,
                EmergencyStatusEnum.CLOSED,
            }:
                raise ValueError("A resolved or closed emergency cannot request additional supply.")

            demand = max(
                0,
                int(emergency.required_quantity or 0)
                - int(emergency.available_quantity or 0),
            )
            if demand <= 0:
                raise ValueError("The emergency has no remaining medicine demand.")

            candidates = self.matching_service.find_emergency_sources(
                medicine_id=emergency.medicine_id,
                requesting_facility_id=emergency.facility_id,
                requested_quantity=demand,
                max_distance_km=emergency.emergency_radius_km,
            )
            if not candidates:
                raise ValueError("No active donor with safe transferable stock was found within the emergency radius.")

            remaining = demand
            created: list[TransferRequest] = []
            now = self._now()
            for candidate in candidates:
                if remaining <= 0:
                    break
                quantity = min(
                    remaining,
                    int(candidate["transferable_quantity"]),
                )
                if quantity <= 0:
                    continue
                transfer = TransferRequest(
                    from_facility_id=UUID(str(candidate["facility_id"])),
                    to_facility_id=emergency.facility_id,
                    medicine_id=emergency.medicine_id,
                    emergency_case_id=emergency.emergency_case_id,
                    requested_quantity=quantity,
                    approved_quantity=None,
                    transfer_status=TransferStatusEnum.PENDING,
                    cascade_safe=True,
                    match_score=candidate["ranking_score"],
                    transfer_distance_km=candidate["distance_km"],
                    recommendation_reason=candidate["recommendation_reason"],
                    requested_by=user.user_id,
                    requested_at=now,
                    completed_at=None,
                )
                self.db.add(transfer)
                created.append(transfer)
                remaining -= quantity

            if not created:
                raise ValueError("No transferable supply could be allocated to this emergency.")

            emergency.emergency_status = EmergencyStatusEnum.MATCHING
            self.db.flush()
            for transfer in created:
                self._record_timeline_event(
                    emergency_case_id=emergency.emergency_case_id,
                    transfer_id=transfer.transfer_id,
                    actor_user_id=user.user_id,
                    event_type="TRANSFER_REQUESTED",
                    title="Supply transfer requested",
                    detail=(
                        f"{transfer.requested_quantity} units of the requested medicine "
                        f"were requested from {transfer.source_facility.facility_name if transfer.source_facility else 'a donor facility'}."
                    ),
                    payload={
                        "requested_quantity": transfer.requested_quantity,
                        "donor_facility_id": str(transfer.from_facility_id),
                        "receiving_facility_id": str(transfer.to_facility_id),
                    },
                    occurred_at=now,
                )
            transfer_ids = [transfer.transfer_id for transfer in created]
            recommended_quantity = sum(transfer.requested_quantity for transfer in created)
            self.db.commit()

            return {
                "emergency_case_id": emergency_case_id,
                "transfer_ids": transfer_ids,
                "recommended_quantity": recommended_quantity,
                "unfilled_quantity": remaining,
                "donor_count": len(created),
                "idempotent_replay": False,
                "message": (
                    "Transfer requests created for hospital review."
                    if remaining == 0
                    else f"Partial network supply identified; {remaining} units remain unsourced."
                ),
            }
        except Exception:
            self.db.rollback()
            raise

    def _get_transfer_for_update(self, transfer_id: UUID) -> TransferRequest:
        transfer = self.db.execute(
            select(TransferRequest)
            .where(TransferRequest.transfer_id == transfer_id)
            .with_for_update()
        ).scalar_one_or_none()
        if transfer is None:
            raise LookupError("Transfer not found.")
        return transfer

    def _locked_inventory(self, facility_id: UUID, medicine_id: UUID) -> InventoryCurrent:
        inventory = self.db.execute(
            select(InventoryCurrent)
            .where(
                InventoryCurrent.facility_id == facility_id,
                InventoryCurrent.medicine_id == medicine_id,
            )
            .with_for_update()
        ).scalar_one_or_none()
        if inventory is None:
            raise ValueError("Required inventory record was not found; no stock changes were applied.")
        return inventory

    @staticmethod
    def _recalculate_inventory(inventory: InventoryCurrent) -> None:
        score = ShortageService.calculate_shortage_score(
            available_stock=int(inventory.available_stock),
            daily_consumption_rate=float(inventory.daily_consumption_rate or 0),
            lead_time_days=int(inventory.lead_time_days or 0),
            safety_stock_days=7,
        )
        inventory.shortage_score = score
        inventory.severity = ShortageService.determine_severity(score)

    def approve_transfer(self, transfer_id: UUID, approved_quantity: int, user) -> dict:
        try:
            transfer = self._get_transfer_for_update(transfer_id)
            self._require_hospital_membership(user, transfer.to_facility_id)
            validate_transfer_transition(transfer.transfer_status, TransferStatusEnum.APPROVED)

            if approved_quantity <= 0:
                raise ValueError("Approved quantity must be greater than zero.")
            if approved_quantity > transfer.requested_quantity:
                raise ValueError("Approved quantity cannot exceed the requested quantity.")

            donor_inventory = self._locked_inventory(
                transfer.from_facility_id, transfer.medicine_id
            )
            medicine = self.db.get(Medicine, transfer.medicine_id)
            if medicine is not None and medicine.requires_cold_chain:
                donor_facility = self.db.get(Facility, transfer.from_facility_id)
                receiving_facility = self.db.get(Facility, transfer.to_facility_id)
                if (
                    donor_facility is None
                    or receiving_facility is None
                    or not donor_facility.cold_chain_capable
                    or not receiving_facility.cold_chain_capable
                ):
                    raise ValueError(
                        "Cold-chain medicine requires declared cold-chain capability at both facilities."
                    )
            # Reserve concrete, unexpired lots in FEFO order. The safety
            # threshold is protected using verified usable lots, not aggregate
            # stock that may include expired or untraceable quantities.
            eligible_batches = self.db.execute(
                select(InventoryBatch)
                .where(
                    InventoryBatch.inventory_id == donor_inventory.inventory_id,
                    InventoryBatch.expiry_date >= date.today(),
                    InventoryBatch.quantity_available > 0,
                )
                .order_by(InventoryBatch.expiry_date.asc(), InventoryBatch.batch_id.asc())
                .with_for_update()
            ).scalars().all()
            if not eligible_batches:
                raise ValueError(
                    "No unexpired, batch-traceable stock is available for this approval."
                )
            safe_batch_quantity = sum(
                int(batch.quantity_available or 0) for batch in eligible_batches
            )
            safe_transferable = safe_transferable_quantity(
                aggregate_available_stock=int(donor_inventory.available_stock or 0),
                minimum_threshold=int(donor_inventory.minimum_threshold or 0),
                unexpired_batch_available=safe_batch_quantity,
            )
            if approved_quantity > safe_transferable:
                raise ValueError(
                    f"Insufficient safe transferable stock after expiry verification. "
                    f"Current safe quantity: {safe_transferable}."
                )

            reservation_plan = plan_fefo_reservation(
                eligible_batches,
                approved_quantity,
                as_of=date.today(),
            )
            for batch, quantity_from_batch in reservation_plan:
                batch.quantity_available -= quantity_from_batch
                batch.quantity_reserved += quantity_from_batch
                self.db.add(
                    TransferBatchAllocation(
                        transfer_id=transfer.transfer_id,
                        batch_id=batch.batch_id,
                        allocated_quantity=quantity_from_batch,
                    )
                )

            donor_inventory.available_stock -= approved_quantity
            donor_inventory.reserved_stock += approved_quantity
            self._recalculate_inventory(donor_inventory)

            transfer.approved_quantity = approved_quantity
            transfer.transfer_status = TransferStatusEnum.APPROVED
            transfer.approved_by = user.user_id
            transfer.approved_at = self._now()
            transfer.cascade_safe = True
            self._record_timeline_event(
                emergency_case_id=transfer.emergency_case_id,
                transfer_id=transfer.transfer_id,
                actor_user_id=user.user_id,
                event_type="TRANSFER_APPROVED",
                title="Hospital approved transfer",
                detail=f"{approved_quantity} units approved; donor inventory and FEFO lots reserved.",
                payload={"approved_quantity": approved_quantity},
                occurred_at=transfer.approved_at,
            )
            self.db.commit()
            self.db.refresh(transfer)
            return self._serialize_transfer(transfer)
        except Exception:
            self.db.rollback()
            raise

    def reject_transfer(self, transfer_id: UUID, reason: str, user) -> dict:
        try:
            transfer = self._get_transfer_for_update(transfer_id)
            self._require_hospital_membership(user, transfer.to_facility_id)
            validate_transfer_transition(transfer.transfer_status, TransferStatusEnum.REJECTED)
            cleaned_reason = reason.strip()
            if len(cleaned_reason) < 5:
                raise ValueError("Rejection reason must contain at least five non-whitespace characters.")

            transfer.transfer_status = TransferStatusEnum.REJECTED
            transfer.approved_by = user.user_id
            transfer.approved_at = self._now()
            transfer.rejection_reason = cleaned_reason
            self._record_timeline_event(
                emergency_case_id=transfer.emergency_case_id,
                transfer_id=transfer.transfer_id,
                actor_user_id=user.user_id,
                event_type="TRANSFER_REJECTED",
                title="Hospital rejected transfer",
                detail=cleaned_reason,
                payload={"reason": cleaned_reason},
                occurred_at=transfer.approved_at,
            )
            self.db.commit()
            self.db.refresh(transfer)
            return {
                "transfer": self._serialize_transfer(transfer),
                "rejection_reason": cleaned_reason,
            }
        except Exception:
            self.db.rollback()
            raise

    def assign_dispatch(
        self,
        transfer_id: UUID,
        transport_type: str,
        vehicle_reference: str | None,
        user,
    ) -> dict:
        try:
            self._require_operations_role(user)
            transfer = self._get_transfer_for_update(transfer_id)
            if transfer.transfer_status != TransferStatusEnum.APPROVED:
                raise ValueError("Only approved transfers can be assigned for dispatch.")

            medicine = self.db.get(Medicine, transfer.medicine_id)
            if medicine is not None and medicine.requires_cold_chain:
                donor_facility = self.db.get(Facility, transfer.from_facility_id)
                receiving_facility = self.db.get(Facility, transfer.to_facility_id)
                if (
                    donor_facility is None
                    or receiving_facility is None
                    or not donor_facility.cold_chain_capable
                    or not receiving_facility.cold_chain_capable
                ):
                    raise ValueError(
                        "Cold-chain transfer requires declared capability at both facilities."
                    )
                if "cold" not in transport_type.strip().lower():
                    raise ValueError(
                        "Assign a cold-chain vehicle for this medicine before dispatch."
                    )

            existing = self.db.execute(
                select(TransferDispatch)
                .where(TransferDispatch.transfer_id == transfer_id)
                .with_for_update()
            ).scalar_one_or_none()
            if existing is not None:
                if existing.status == DispatchStatusEnum.ASSIGNED:
                    self.db.commit()
                    return {
                        "transfer_id": transfer_id,
                        "dispatch_id": existing.dispatch_id,
                        "dispatch_status": existing.status.value,
                        "idempotent_replay": True,
                    }
                raise ValueError("A dispatch record already exists for this transfer.")

            dispatch = TransferDispatch(
                transfer_id=transfer_id,
                dispatcher_id=user.user_id,
                transport_type=transport_type.strip(),
                vehicle_reference=vehicle_reference.strip() if vehicle_reference else None,
                status=DispatchStatusEnum.ASSIGNED,
            )
            self.db.add(dispatch)
            self.db.flush()
            self._record_timeline_event(
                emergency_case_id=transfer.emergency_case_id,
                transfer_id=transfer.transfer_id,
                actor_user_id=user.user_id,
                event_type="DISPATCH_ASSIGNED",
                title="Transport assigned",
                detail=f"{dispatch.transport_type}" + (f" — {dispatch.vehicle_reference}" if dispatch.vehicle_reference else ""),
                payload={
                    "transport_type": dispatch.transport_type,
                    "vehicle_reference": dispatch.vehicle_reference,
                },
            )
            self.db.commit()
            self.db.refresh(dispatch)
            return {
                "transfer_id": transfer_id,
                "dispatch_id": dispatch.dispatch_id,
                "dispatch_status": dispatch.status.value,
                "transport_type": dispatch.transport_type,
                "vehicle_reference": dispatch.vehicle_reference,
                "idempotent_replay": False,
            }
        except Exception:
            self.db.rollback()
            raise

    def dispatch_transfer_by_id(self, transfer_id: UUID, user) -> dict:
        try:
            self._require_operations_role(user)
            transfer = self._get_transfer_for_update(transfer_id)
            dispatch = self.db.execute(
                select(TransferDispatch)
                .where(TransferDispatch.transfer_id == transfer_id)
                .with_for_update()
            ).scalar_one_or_none()
            if dispatch is None:
                raise ValueError("Assign transport before dispatching this transfer.")

            if transfer.transfer_status == TransferStatusEnum.IN_TRANSIT:
                return {
                    "transfer_id": transfer_id,
                    "transfer_status": transfer.transfer_status.value,
                    "dispatch_status": dispatch.status.value,
                    "idempotent_replay": True,
                }

            validate_transfer_transition(
                transfer.transfer_status,
                TransferStatusEnum.IN_TRANSIT,
            )
            if dispatch.status != DispatchStatusEnum.ASSIGNED:
                raise ValueError("Only an assigned dispatch can enter transit.")

            now = self._now()
            dispatch.status = DispatchStatusEnum.IN_TRANSIT
            dispatch.dispatched_at = now
            transfer.transfer_status = TransferStatusEnum.IN_TRANSIT
            self._record_timeline_event(
                emergency_case_id=transfer.emergency_case_id,
                transfer_id=transfer.transfer_id,
                actor_user_id=user.user_id,
                event_type="SHIPMENT_DISPATCHED",
                title="Shipment entered transit",
                detail=f"Shipment dispatched via {dispatch.transport_type}.",
                payload={
                    "transport_type": dispatch.transport_type,
                    "vehicle_reference": dispatch.vehicle_reference,
                },
                occurred_at=now,
            )
            self.db.commit()
            return {
                "transfer_id": transfer_id,
                "transfer_status": transfer.transfer_status.value,
                "dispatch_status": dispatch.status.value,
                "dispatched_at": now,
                "idempotent_replay": False,
            }
        except Exception:
            self.db.rollback()
            raise

    def mark_transfer_delivered(self, transfer_id: UUID, user) -> dict:
        try:
            self._require_operations_role(user)
            transfer = self._get_transfer_for_update(transfer_id)

            # A retried delivery confirmation is a no-op: never settle stock twice.
            if transfer.transfer_status == TransferStatusEnum.COMPLETED:
                dispatch = self.db.execute(
                    select(TransferDispatch).where(
                        TransferDispatch.transfer_id == transfer_id
                    )
                ).scalar_one_or_none()
                return {
                    "transfer_id": transfer_id,
                    "transfer_status": TransferStatusEnum.COMPLETED.value,
                    "dispatch_status": dispatch.status.value if dispatch else None,
                    "idempotent_replay": True,
                }

            validate_transfer_transition(
                transfer.transfer_status, TransferStatusEnum.COMPLETED
            )
            if transfer.approved_quantity is None or transfer.approved_quantity <= 0:
                raise ValueError("Transfer has no valid approved quantity.")

            dispatch = self.db.execute(
                select(TransferDispatch)
                .where(TransferDispatch.transfer_id == transfer_id)
                .with_for_update()
            ).scalar_one_or_none()
            if dispatch is None or dispatch.status != DispatchStatusEnum.IN_TRANSIT:
                raise ValueError("Only an in-transit shipment can be marked delivered.")

            # Lock donor and destination in stable order to reduce deadlock risk.
            facility_ids = sorted(
                [transfer.from_facility_id, transfer.to_facility_id],
                key=str,
            )
            locked_rows = self.db.execute(
                select(InventoryCurrent)
                .where(
                    InventoryCurrent.facility_id.in_(facility_ids),
                    InventoryCurrent.medicine_id == transfer.medicine_id,
                )
                .order_by(InventoryCurrent.facility_id)
                .with_for_update()
            ).scalars().all()
            inventory_by_facility = {
                row.facility_id: row for row in locked_rows
            }
            donor = inventory_by_facility.get(transfer.from_facility_id)
            destination = inventory_by_facility.get(transfer.to_facility_id)
            if donor is None or destination is None:
                raise ValueError("Donor and destination inventory records must exist before delivery.")

            quantity = transfer.approved_quantity
            if donor.reserved_stock < quantity or donor.total_stock < quantity:
                raise ValueError("Donor reserved/total stock is inconsistent; delivery settlement was cancelled.")

            now = self._now()
            batch_allocations = self.db.execute(
                select(TransferBatchAllocation, InventoryBatch)
                .join(
                    InventoryBatch,
                    TransferBatchAllocation.batch_id == InventoryBatch.batch_id,
                )
                .where(TransferBatchAllocation.transfer_id == transfer_id)
                .order_by(InventoryBatch.expiry_date.asc(), InventoryBatch.batch_id.asc())
                .with_for_update()
            ).all()

            allocated_batch_quantity = sum(
                int(allocation.allocated_quantity) for allocation, _ in batch_allocations
            )
            if batch_allocations and allocated_batch_quantity != quantity:
                raise ValueError(
                    "Batch allocation total does not match the approved transfer quantity."
                )

            if not batch_allocations:
                tracked_batch_count = self.db.execute(
                    select(func.count(InventoryBatch.batch_id)).where(
                        InventoryBatch.inventory_id == donor.inventory_id
                    )
                ).scalar_one()
                if tracked_batch_count:
                    raise ValueError(
                        "Tracked donor stock has no transfer batch allocation; settlement was cancelled."
                    )

            donor.reserved_stock -= quantity
            donor.total_stock -= quantity
            destination.available_stock += quantity
            destination.total_stock += quantity
            destination.last_restocked_at = now

            # Preserve lot identity and expiry metadata at the receiving facility.
            for allocation, source_batch in batch_allocations:
                lot_quantity = int(allocation.allocated_quantity)
                if int(source_batch.quantity_reserved or 0) < lot_quantity:
                    raise ValueError(
                        f"Reserved quantity is inconsistent for batch {source_batch.batch_number}."
                    )
                source_batch.quantity_reserved -= lot_quantity
                self.db.add(
                    InventoryBatch(
                        inventory_id=destination.inventory_id,
                        batch_number=source_batch.batch_number,
                        supplier_name=source_batch.supplier_name,
                        manufacturing_date=source_batch.manufacturing_date,
                        expiry_date=source_batch.expiry_date,
                        quantity_received=lot_quantity,
                        quantity_available=lot_quantity,
                        quantity_reserved=0,
                        unit_cost=source_batch.unit_cost,
                    )
                )

            self._recalculate_inventory(donor)
            self._recalculate_inventory(destination)

            transfer.transfer_status = TransferStatusEnum.COMPLETED
            transfer.completed_at = now
            dispatch.status = DispatchStatusEnum.DELIVERED
            dispatch.delivered_at = now
            self._record_timeline_event(
                emergency_case_id=transfer.emergency_case_id,
                transfer_id=transfer.transfer_id,
                actor_user_id=user.user_id,
                event_type="SHIPMENT_DELIVERED",
                title="Delivery confirmed",
                detail=f"{quantity} units delivered; destination inventory and batch records settled.",
                payload={"delivered_quantity": quantity},
                occurred_at=now,
            )

            emergency_payload = None
            if transfer.emergency_case_id:
                emergency = self.db.execute(
                    select(EmergencyCase)
                    .where(EmergencyCase.emergency_case_id == transfer.emergency_case_id)
                    .with_for_update()
                ).scalar_one_or_none()
                if emergency is not None:
                    # The emergency stores its target quantity and its current
                    # available quantity at the receiving facility. Reflect this
                    # delivery before deciding whether the target is satisfied.
                    emergency.available_quantity = (
                        int(emergency.available_quantity or 0) + quantity
                    )
                    self.db.flush()

                    completed_quantity = self.db.execute(
                        select(func.coalesce(func.sum(TransferRequest.approved_quantity), 0))
                        .where(
                            TransferRequest.emergency_case_id == transfer.emergency_case_id,
                            TransferRequest.transfer_status == TransferStatusEnum.COMPLETED,
                        )
                    ).scalar_one()
                    fulfilled_transfer_quantity = int(completed_quantity or 0)
                    required = int(emergency.required_quantity or 0)
                    if int(emergency.available_quantity or 0) >= required and required > 0:
                        emergency.emergency_status = EmergencyStatusEnum.RESOLVED
                        emergency.resolved_at = now
                    elif fulfilled_transfer_quantity > 0:
                        emergency.emergency_status = EmergencyStatusEnum.PARTIALLY_RESOLVED
                        emergency.resolved_at = None
                    emergency_payload = {
                        "emergency_case_id": emergency.emergency_case_id,
                        "available_quantity": int(emergency.available_quantity or 0),
                        "completed_transfer_quantity": fulfilled_transfer_quantity,
                        "required_quantity": required,
                        "status": emergency.emergency_status.value,
                    }
                    if emergency.emergency_status == EmergencyStatusEnum.RESOLVED:
                        self._record_timeline_event(
                            emergency_case_id=emergency.emergency_case_id,
                            transfer_id=transfer.transfer_id,
                            actor_user_id=user.user_id,
                            event_type="EMERGENCY_RESOLVED",
                            title="Emergency target fulfilled",
                            detail=f"Receiving facility now has {emergency.available_quantity} units against a {required}-unit target.",
                            payload={
                                "available_quantity": int(emergency.available_quantity or 0),
                                "required_quantity": required,
                            },
                            occurred_at=now,
                        )
                    elif emergency.emergency_status == EmergencyStatusEnum.PARTIALLY_RESOLVED:
                        self._record_timeline_event(
                            emergency_case_id=emergency.emergency_case_id,
                            transfer_id=transfer.transfer_id,
                            actor_user_id=user.user_id,
                            event_type="EMERGENCY_PARTIALLY_RESOLVED",
                            title="Emergency partially fulfilled",
                            detail=f"Receiving facility has {emergency.available_quantity} units against a {required}-unit target.",
                            payload={
                                "available_quantity": int(emergency.available_quantity or 0),
                                "required_quantity": required,
                            },
                            occurred_at=now,
                        )

            self.db.commit()
            return {
                "transfer_id": transfer_id,
                "transfer_status": TransferStatusEnum.COMPLETED.value,
                "dispatch_status": DispatchStatusEnum.DELIVERED.value,
                "delivered_quantity": quantity,
                "delivered_at": now,
                "emergency_fulfillment": emergency_payload,
                "idempotent_replay": False,
            }
        except Exception:
            self.db.rollback()
            raise

    def dispatch_transfer(self, emergency_case_id, user=None):
        """Deprecated compatibility shim: create transfer requests, never dispatch stock."""
        if user is None:
            raise PermissionError("Authentication is required to request transfer.")
        return self.request_transfer_from_emergency(emergency_case_id, user)

    # Read APIs enforce network or hospital scope instead of exposing every
    # organization's transfer records to any logged-in user.
    def _facility_ids_for_hospital_admin(self, user) -> list[UUID]:
        return list(
            self.db.execute(
                select(FacilityUser.facility_id).where(
                    FacilityUser.user_id == user.user_id,
                    FacilityUser.assigned_role == UserRoleEnum.HOSPITAL_ADMIN,
                )
            ).scalars().all()
        )

    def get_all_transfers_for_user(self, user) -> list[dict]:
        from app.repositories.redistribution_repository import RedistributionRepository

        if user.role in {UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR}:
            return RedistributionRepository(self.db).get_all_transfers()
        if user.role == UserRoleEnum.HOSPITAL_ADMIN:
            facility_ids = self._facility_ids_for_hospital_admin(user)
            if not facility_ids:
                raise PermissionError("No hospital facility is assigned to this administrator.")
            return RedistributionRepository(self.db).get_transfers_for_facilities(facility_ids)
        raise PermissionError("This role cannot view transfer records.")

    def get_high_priority_transfers_for_user(self, user) -> list[dict]:
        transfers = self.get_all_transfers_for_user(user)
        return [
            transfer for transfer in transfers
            if transfer.get("match_score") is not None
            and float(transfer["match_score"]) >= 80
        ]

    def get_facility_transfers_for_user(self, facility_id: UUID, user) -> list[dict]:
        from app.repositories.redistribution_repository import RedistributionRepository

        if user.role in {UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR}:
            return RedistributionRepository(self.db).get_transfers_for_facility(facility_id)
        if user.role == UserRoleEnum.HOSPITAL_ADMIN:
            if facility_id not in self._facility_ids_for_hospital_admin(user):
                raise PermissionError("Hospital administrators may only view transfers for their assigned facility.")
            return RedistributionRepository(self.db).get_transfers_for_facility(facility_id)
        raise PermissionError("This role cannot view facility transfer records.")

    def get_dashboard_for_user(self, user) -> dict:
        transfers = self.get_all_transfers_for_user(user)
        scores = [
            float(transfer["match_score"])
            for transfer in transfers
            if transfer.get("match_score") is not None
        ]
        return {
            "total_transfers": len(transfers),
            "pending": sum(transfer["transfer_status"] == TransferStatusEnum.PENDING for transfer in transfers),
            "approved": sum(transfer["transfer_status"] == TransferStatusEnum.APPROVED for transfer in transfers),
            "in_transit": sum(transfer["transfer_status"] == TransferStatusEnum.IN_TRANSIT for transfer in transfers),
            "completed": sum(transfer["transfer_status"] == TransferStatusEnum.COMPLETED for transfer in transfers),
            "high_priority": sum(score >= 80 for score in scores),
            "average_match_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
        }

    # Compatibility service methods for trusted internal callers.
    def get_all_transfers(self):
        from app.repositories.redistribution_repository import RedistributionRepository
        return RedistributionRepository(self.db).get_all_transfers()

    def get_high_priority_transfers(self):
        from app.repositories.redistribution_repository import RedistributionRepository
        return RedistributionRepository(self.db).get_high_priority_transfers()

    def get_facility_transfers(self, facility_id):
        from app.repositories.redistribution_repository import RedistributionRepository
        return RedistributionRepository(self.db).get_transfers_for_facility(facility_id)

    def get_dashboard(self):
        from app.repositories.redistribution_repository import RedistributionRepository
        return RedistributionRepository(self.db).get_dashboard()
