from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import TransferStatusEnum
from app.models.dispatch import DispatchStatusEnum, TransferDispatch
from app.models.inventory import InventoryCurrent
from app.models.redistribution import TransferRequest
from app.services.emergency.emergency_service import EmergencyService
from app.services.governance.audit_service import AuditService


class DispatchService:

    def __init__(self, db: Session):
        self.db = db

    def assign_dispatch(
        self,
        transfer_id: UUID,
        dispatcher_id: UUID,
        transport_type: str,
        vehicle_reference: str | None = None,
    ):

        transfer = (
            self.db.query(TransferRequest)
            .filter(
                TransferRequest.transfer_id == transfer_id
            )
            .with_for_update()
            .first()
        )

        if transfer is None:
            raise ValueError("Transfer not found.")

        if transfer.transfer_status != TransferStatusEnum.APPROVED:
            raise ValueError(
                "Only approved transfers can be dispatched."
            )

        existing = (
            self.db.query(TransferDispatch)
            .filter(
                TransferDispatch.transfer_id == transfer_id
            )
            .first()
        )

        if existing:
            raise ValueError(
                "Dispatch already exists for this transfer."
            )

        dispatch = TransferDispatch(
            transfer_id=transfer_id,
            dispatcher_id=dispatcher_id,
            transport_type=transport_type,
            vehicle_reference=vehicle_reference,
            status=DispatchStatusEnum.ASSIGNED,
        )

        self.db.add(dispatch)
        self.db.flush()

        self._record_transfer_event(
            transfer,
            "DISPATCH_ASSIGNED",
            dispatcher_id,
            {"transport_type": transport_type, "vehicle_reference": vehicle_reference},
        )

        return dispatch

    def dispatch_transfer(
        self,
        transfer_id: UUID,
    ):

        dispatch = (
            self.db.query(TransferDispatch)
            .filter(
                TransferDispatch.transfer_id == transfer_id
            )
            .with_for_update()
            .first()
        )

        if dispatch is None:
            raise ValueError(
                "Dispatch assignment not found."
            )

        if dispatch.status != DispatchStatusEnum.ASSIGNED:
            raise ValueError(
                "Dispatch is not ready for departure."
            )

        transfer = (
            self.db.query(TransferRequest)
            .filter(
                TransferRequest.transfer_id == transfer_id
            )
            .with_for_update()
            .first()
        )

        if transfer is None:
            raise ValueError("Transfer not found.")

        now = datetime.now(timezone.utc)

        dispatch.status = DispatchStatusEnum.IN_TRANSIT
        dispatch.dispatched_at = now

        transfer.transfer_status = TransferStatusEnum.IN_TRANSIT

        self._record_transfer_event(
            transfer,
            "TRANSFER_DISPATCHED",
            dispatch.dispatcher_id,
            {"dispatched_at": now.isoformat()},
        )

        self.db.flush()

        return dispatch

    def mark_delivered(
        self,
        transfer_id: UUID,
    ):

        dispatch = (
            self.db.query(TransferDispatch)
            .filter(
                TransferDispatch.transfer_id == transfer_id
            )
            .with_for_update()
            .first()
        )

        if dispatch is None:
            raise ValueError(
                "Dispatch record not found."
            )

        if dispatch.status != DispatchStatusEnum.IN_TRANSIT:
            raise ValueError(
                "Only in-transit shipments can be delivered."
            )

        transfer = (
            self.db.query(TransferRequest)
            .filter(
                TransferRequest.transfer_id == transfer_id
            )
            .with_for_update()
            .first()
        )

        if transfer is None:
            raise ValueError("Transfer not found.")

        if transfer.approved_quantity is None or transfer.approved_quantity <= 0:
            raise ValueError("Approved transfer quantity is required for delivery.")

        inventories = (
            self.db.query(InventoryCurrent)
            .filter(
                InventoryCurrent.facility_id.in_([
                    transfer.from_facility_id,
                    transfer.to_facility_id,
                ]),
                InventoryCurrent.medicine_id == transfer.medicine_id,
            )
            .order_by(InventoryCurrent.inventory_id)
            .with_for_update()
            .all()
        )
        inventory_by_facility = {
            inventory.facility_id: inventory for inventory in inventories
        }
        source_inventory = inventory_by_facility.get(transfer.from_facility_id)
        destination_inventory = inventory_by_facility.get(transfer.to_facility_id)

        if source_inventory is None or destination_inventory is None:
            raise ValueError("Source and destination inventory records are required for delivery.")

        quantity = transfer.approved_quantity
        if source_inventory.reserved_stock < quantity:
            raise ValueError("Reserved donor inventory is insufficient for delivery.")

        now = datetime.now(timezone.utc)

        dispatch.status = DispatchStatusEnum.DELIVERED
        dispatch.delivered_at = now

        source_inventory.reserved_stock -= quantity
        source_inventory.total_stock -= quantity
        destination_inventory.available_stock += quantity
        destination_inventory.total_stock += quantity

        self._record_transfer_event(
            transfer,
            "TRANSFER_DELIVERED",
            dispatch.dispatcher_id,
            {"delivered_at": now.isoformat(), "quantity": quantity},
        )
        self._record_transfer_event(
            transfer,
            "INVENTORY_SETTLED",
            dispatch.dispatcher_id,
            {"quantity": quantity},
        )

        transfer.transfer_status = TransferStatusEnum.COMPLETED
        transfer.completed_at = now

        if transfer.emergency_case_id is not None:
            emergency_service = EmergencyService(self.db)
            emergency_service.update_emergency_fulfillment(
                transfer.emergency_case_id,
            )

        self.db.flush()

        return dispatch

    def _record_transfer_event(
        self,
        transfer: TransferRequest,
        action_type: str,
        user_id: UUID | None,
        new_value: dict,
    ):
        AuditService(self.db).record_event(
            action_type=action_type,
            entity_type="EMERGENCY" if transfer.emergency_case_id else "TRANSFER",
            entity_id=transfer.emergency_case_id or transfer.transfer_id,
            user_id=user_id,
            new_value=new_value,
        )
