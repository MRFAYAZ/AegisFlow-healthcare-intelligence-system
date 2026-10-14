from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from app.core.enums import (
    AllocationLineStatusEnum,
    AllocationPlanStatusEnum,
    TransferStatusEnum,
    UserRoleEnum,
)
from app.models.allocation import (
    EmergencyAllocationLine,
    EmergencyAllocationPlan,
)
from app.models.emergency import EmergencyCase, EmergencySourceMatch
from app.models.facility_user import FacilityUser
from app.models.inventory import InventoryCurrent
from app.models.redistribution import TransferRequest
from app.models.user import User
from app.services.governance.audit_service import AuditService


class AllocationService:
    """Deterministically turn ranked source matches into an allocation plan."""

    def __init__(self, db: Session):
        self.db = db

    def generate_allocation_plan(
        self,
        emergency_case_id: UUID,
    ) -> EmergencyAllocationPlan:
        emergency = (
            self.db.query(EmergencyCase)
            .filter(EmergencyCase.emergency_case_id == emergency_case_id)
            .with_for_update()
            .first()
        )

        if emergency is None:
            raise ValueError("Emergency case not found.")

        if emergency.required_quantity is None:
            raise ValueError("Emergency case has no required quantity.")

        required_quantity = int(emergency.required_quantity)
        if required_quantity <= 0:
            raise ValueError(
                "Emergency required quantity must be greater than zero."
            )

        existing_plan = (
            self.db.query(EmergencyAllocationPlan)
            .filter(
                EmergencyAllocationPlan.emergency_case_id == emergency_case_id,
                EmergencyAllocationPlan.status.in_(
                    [
                        AllocationPlanStatusEnum.DRAFT,
                        AllocationPlanStatusEnum.RECOMMENDED,
                        AllocationPlanStatusEnum.PENDING_APPROVAL,
                        AllocationPlanStatusEnum.PARTIALLY_APPROVED,
                        AllocationPlanStatusEnum.APPROVED,
                        AllocationPlanStatusEnum.PARTIALLY_FULFILLED,
                    ]
                ),
            )
            .first()
        )
        if existing_plan is not None:
            return existing_plan

        matches = (
            self.db.query(EmergencySourceMatch)
            .filter(
                EmergencySourceMatch.emergency_case_id == emergency_case_id,
                EmergencySourceMatch.transferable_quantity > 0,
            )
            .order_by(
                EmergencySourceMatch.ranking_score.desc(),
                EmergencySourceMatch.distance_km.asc(),
            )
            .all()
        )
        if not matches:
            raise ValueError("No eligible emergency source matches found.")

        remaining_quantity = required_quantity
        lines: list[EmergencyAllocationLine] = []

        for match in matches:
            if remaining_quantity <= 0:
                break

            safe_quantity = int(match.transferable_quantity or 0)
            if safe_quantity <= 0:
                continue

            allocated_quantity = min(safe_quantity, remaining_quantity)
            if allocated_quantity <= 0:
                continue

            lines.append(
                EmergencyAllocationLine(
                    source_facility_id=match.source_facility_id,
                    medicine_id=match.medicine_id,
                    match_id=match.match_id,
                    recommended_quantity=allocated_quantity,
                    approved_quantity=0,
                    source_available_quantity=int(match.available_quantity or 0),
                    source_safe_transferable_quantity=safe_quantity,
                    distance_km=match.distance_km,
                    allocation_score=match.ranking_score,
                    allocation_reason=self._build_reason(match),
                    status=AllocationLineStatusEnum.RECOMMENDED,
                )
            )
            remaining_quantity -= allocated_quantity

        recommended_quantity = required_quantity - remaining_quantity
        if recommended_quantity == 0:
            raise ValueError(
                "Unable to allocate any quantity from eligible sources."
            )

        fulfillment_percentage = (
            Decimal(recommended_quantity) / Decimal(required_quantity) * Decimal("100")
        )
        plan = EmergencyAllocationPlan(
            emergency_case_id=emergency_case_id,
            medicine_id=emergency.medicine_id,
            requested_quantity=required_quantity,
            recommended_quantity=recommended_quantity,
            allocated_quantity=0,
            fulfillment_percentage=fulfillment_percentage,
            optimization_score=self._calculate_plan_score(lines),
            status=AllocationPlanStatusEnum.RECOMMENDED,
            recommendation_reason=self._build_plan_reason(
                required_quantity,
                recommended_quantity,
                len(lines),
            ),
        )

        self.db.add(plan)
        self.db.flush()

        for line in lines:
            line.allocation_plan_id = plan.allocation_plan_id
            self.db.add(line)

        self.db.flush()

        AuditService(self.db).record_event(
            action_type="ALLOCATION_RECOMMENDED",
            entity_type="EMERGENCY",
            entity_id=emergency_case_id,
            new_value={
                "recommended_quantity": recommended_quantity,
                "required_quantity": required_quantity,
                "source_count": len(lines),
            },
        )
        return plan

    def get_allocation_plan(
        self,
        emergency_case_id: UUID,
    ) -> EmergencyAllocationPlan:
        plan = (
            self.db.query(EmergencyAllocationPlan)
            .filter(EmergencyAllocationPlan.emergency_case_id == emergency_case_id)
            .first()
        )
        if plan is None:
            raise ValueError("Allocation plan not found.")
        return plan

    def get_allocation_plan_with_lines(
        self,
        emergency_case_id: UUID,
    ) -> EmergencyAllocationPlan:
        plan = (
            self.db.query(EmergencyAllocationPlan)
            .options(selectinload(EmergencyAllocationPlan.allocation_lines))
            .filter(EmergencyAllocationPlan.emergency_case_id == emergency_case_id)
            .first()
        )
        if plan is None:
            raise ValueError("Allocation plan not found.")
        return plan

    def get_authorized_allocation_plan(
        self,
        emergency_case_id: UUID,
        current_user: User,
    ) -> EmergencyAllocationPlan:
        emergency = (
            self.db.query(EmergencyCase)
            .filter(EmergencyCase.emergency_case_id == emergency_case_id)
            .first()
        )
        if emergency is None:
            raise ValueError("Emergency case not found.")

        try:
            role = AllocationService._user_role(current_user)
        except (TypeError, ValueError):
            raise PermissionError("User has an invalid application role.")

        if role == UserRoleEnum.HOSPITAL_ADMIN:
            if not self._user_can_access_emergency(
                current_user.user_id,
                emergency,
            ):
                raise PermissionError(
                    "Hospital administrator is not authorized for this emergency."
                )
        elif role not in {
            UserRoleEnum.EMERGENCY_OPERATOR,
            UserRoleEnum.SYSTEM_ADMIN,
        }:
            raise PermissionError("Access denied.")

        return self.get_allocation_plan_with_lines(emergency_case_id)

    def approve_allocation(
        self,
        emergency_case_id: UUID,
        approvals: list[tuple[UUID, int]],
        approver: User,
    ) -> tuple[EmergencyAllocationPlan, list[UUID]]:
        role = UserRoleEnum(approver.role)
        if role != UserRoleEnum.HOSPITAL_ADMIN:
            raise PermissionError("Only hospital administrators can approve allocations.")
        if not approvals:
            raise ValueError("At least one allocation line is required.")
        emergency = (
            self.db.query(EmergencyCase)
            .filter(EmergencyCase.emergency_case_id == emergency_case_id)
            .with_for_update()
            .first()
        )
        if emergency is None:
            raise ValueError("Emergency case not found.")
        if not self._user_can_access_emergency(approver.user_id, emergency):
            raise PermissionError(
                "Hospital administrator is not authorized for this emergency."
            )

        plan = (
            self.db.query(EmergencyAllocationPlan)
            .options(selectinload(EmergencyAllocationPlan.allocation_lines))
            .filter(EmergencyAllocationPlan.emergency_case_id == emergency_case_id)
            .with_for_update()
            .first()
        )
        if plan is None:
            raise ValueError("Allocation plan not found.")
        if plan.status not in {
            AllocationPlanStatusEnum.RECOMMENDED,
            AllocationPlanStatusEnum.PENDING_APPROVAL,
            AllocationPlanStatusEnum.PARTIALLY_APPROVED,
        }:
            raise ValueError(
                f"Allocation plan cannot be approved from status {plan.status}."
            )

        requested = dict(approvals)
        if any(quantity <= 0 for quantity in requested.values()):
            raise ValueError("Approved quantities must be greater than zero.")

        lines_by_id = {line.allocation_line_id: line for line in plan.allocation_lines}
        if set(requested) - set(lines_by_id):
            raise ValueError("Allocation line does not belong to this plan.")

        existing_transfers = {
            transfer.from_facility_id: transfer
            for transfer in self.db.query(TransferRequest)
            .filter(TransferRequest.emergency_case_id == emergency_case_id)
            .with_for_update()
            .all()
        }

        transfer_ids: list[UUID] = []
        for line_id, quantity in requested.items():
            line = lines_by_id[line_id]
            if quantity > line.recommended_quantity:
                raise ValueError("Approved quantity cannot exceed the recommended quantity.")
            if quantity > line.source_safe_transferable_quantity:
                raise ValueError("Approved quantity exceeds the safe transferable quantity.")

            existing_transfer = existing_transfers.get(line.source_facility_id)
            if existing_transfer is not None:
                if existing_transfer.requested_quantity != quantity:
                    raise ValueError(
                        "An existing transfer already uses a different quantity "
                        "for this donor facility."
                    )
                if existing_transfer.transfer_status == TransferStatusEnum.APPROVED:
                    transfer_ids.append(existing_transfer.transfer_id)
                    line.approved_quantity = quantity
                    line.status = AllocationLineStatusEnum.APPROVED
                    continue

            inventory = (
                self.db.query(InventoryCurrent)
                .filter(
                    InventoryCurrent.facility_id == line.source_facility_id,
                    InventoryCurrent.medicine_id == line.medicine_id,
                )
                .with_for_update()
                .first()
            )
            if inventory is None:
                raise ValueError("Donor inventory record not found.")
            if inventory.available_stock < quantity:
                raise ValueError("Donor no longer has sufficient available stock.")
            if inventory.available_stock - quantity < inventory.minimum_threshold:
                raise ValueError(
                    "Approval would reduce donor inventory below its minimum threshold."
                )

            inventory.available_stock -= quantity
            inventory.reserved_stock += quantity
            line.approved_quantity = quantity
            line.status = AllocationLineStatusEnum.APPROVED

            now = datetime.now(timezone.utc)
            if existing_transfer is None:
                existing_transfer = TransferRequest(
                    from_facility_id=line.source_facility_id,
                    to_facility_id=emergency.facility_id,
                    medicine_id=line.medicine_id,
                    emergency_case_id=emergency_case_id,
                    requested_quantity=quantity,
                    requested_by=approver.user_id,
                    requested_at=now,
                )
                self.db.add(existing_transfer)

            existing_transfer.approved_quantity = quantity
            existing_transfer.transfer_status = TransferStatusEnum.APPROVED
            existing_transfer.cascade_safe = True
            existing_transfer.match_score = line.allocation_score
            existing_transfer.transfer_distance_km = line.distance_km
            existing_transfer.recommendation_reason = line.allocation_reason
            existing_transfer.approved_by = approver.user_id
            existing_transfer.approved_at = now
            self.db.flush()
            transfer_ids.append(existing_transfer.transfer_id)
            existing_transfers[line.source_facility_id] = existing_transfer

        total_approved = sum(
            line.approved_quantity or 0
            for line in plan.allocation_lines
        )
        plan.allocated_quantity = total_approved
        plan.fulfillment_percentage = (
            Decimal(total_approved)
            / Decimal(plan.requested_quantity)
            * Decimal("100")
        )
        plan.approved_by = approver.user_id
        plan.approved_at = datetime.now(timezone.utc)
        plan.status = (
            AllocationPlanStatusEnum.APPROVED
            if total_approved >= plan.recommended_quantity
            else AllocationPlanStatusEnum.PARTIALLY_APPROVED
        )
        self.db.flush()
        return plan, transfer_ids

    def _user_can_access_emergency(
        self,
        user_id: UUID,
        emergency: EmergencyCase,
    ) -> bool:
        memberships = (
            self.db.query(FacilityUser)
            .filter(FacilityUser.user_id == user_id)
            .all()
        )
        return any(
            membership.facility_id == emergency.facility_id
            for membership in memberships
        )

    def reject_allocation(
        self,
        emergency_case_id: UUID,
        approver: User,
    ) -> EmergencyAllocationPlan:
        plan = self.get_authorized_allocation_plan(emergency_case_id, approver)
        if UserRoleEnum(approver.role) != UserRoleEnum.HOSPITAL_ADMIN:
            raise PermissionError("Only hospital administrators can reject allocations.")
        if plan.status not in {
            AllocationPlanStatusEnum.RECOMMENDED,
            AllocationPlanStatusEnum.PENDING_APPROVAL,
            AllocationPlanStatusEnum.PARTIALLY_APPROVED,
        }:
            raise ValueError("Allocation plan is not pending approval.")

        plan.status = AllocationPlanStatusEnum.CANCELLED
        for line in plan.allocation_lines:
            line.status = AllocationLineStatusEnum.CANCELLED
        self.db.flush()
        return plan

    @staticmethod
    def _user_role(current_user: User):
        return UserRoleEnum(current_user.role)

    @staticmethod
    def _build_reason(match: EmergencySourceMatch) -> str:
        return (
            f"Selected based on ranking score {float(match.ranking_score or 0):.2f}, "
            f"distance {float(match.distance_km or 0):.2f} km, and safe "
            f"transferable quantity {int(match.transferable_quantity or 0)}."
        )

    @staticmethod
    def _calculate_plan_score(
        lines: list[EmergencyAllocationLine],
    ) -> Decimal:
        if not lines:
            return Decimal("0")

        scores = [Decimal(str(line.allocation_score or 0)) for line in lines]
        return sum(scores) / Decimal(len(scores))

    @staticmethod
    def _build_plan_reason(
        required_quantity: int,
        recommended_quantity: int,
        source_count: int,
    ) -> str:
        percentage = recommended_quantity / required_quantity * 100
        if recommended_quantity >= required_quantity:
            return (
                f"Full emergency demand of {required_quantity} units can be "
                f"fulfilled using {source_count} source facility(s)."
            )

        return (
            f"{recommended_quantity} of {required_quantity} units can currently "
            f"be fulfilled using {source_count} source facility(s), representing "
            f"{percentage:.1f}% fulfillment."
        )