from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import (
    TransferStatusEnum,
    UserRoleEnum,
)

from app.models.user import User

from app.repositories.facility_user_repository import (
    FacilityUserRepository,
)

from app.repositories.inventory_repository import (
    InventoryRepository,
)

from app.repositories.redistribution_repository import (
    RedistributionRepository,
)

from app.services.governance.audit_service import AuditService


class RedistributionService:

    def __init__(
        self,
        db: Session,
    ):

        self.db = db

        self.inventory_repository = (
            InventoryRepository(db)
        )

        self.redistribution_repository = (
            RedistributionRepository(db)
        )

        self.facility_user_repository = (
            FacilityUserRepository(db)
        )

    # =====================================================
    # TRANSFER STATE MACHINE
    # =====================================================

    ALLOWED_TRANSFER_TRANSITIONS = {

        TransferStatusEnum.PENDING: {
            TransferStatusEnum.APPROVED,
            TransferStatusEnum.REJECTED,
        },

        TransferStatusEnum.APPROVED: {
            TransferStatusEnum.IN_TRANSIT,
            TransferStatusEnum.CANCELLED,
        },

        TransferStatusEnum.IN_TRANSIT: {
            TransferStatusEnum.COMPLETED,
            TransferStatusEnum.CANCELLED,
        },

        TransferStatusEnum.REJECTED: set(),

        TransferStatusEnum.COMPLETED: set(),

        TransferStatusEnum.CANCELLED: set(),
    }

    # =====================================================
    # VALIDATE TRANSFER STATE TRANSITION
    # =====================================================

    def validate_transfer_transition(
        self,
        current_status: TransferStatusEnum,
        new_status: TransferStatusEnum,
    ) -> None:

        allowed_statuses = (
            self.ALLOWED_TRANSFER_TRANSITIONS.get(
                current_status,
                set(),
            )
        )

        if new_status not in allowed_statuses:

            raise ValueError(
                "Invalid transfer status transition: "
                f"{current_status.value} -> "
                f"{new_status.value}"
            )

    # =====================================================
    # VALIDATE QUANTITY
    # =====================================================

    def validate_quantity(
        self,
        quantity: int,
    ) -> None:

        if quantity <= 0:

            raise ValueError(
                "Transfer quantity must be greater than zero."
            )

    # =====================================================
    # VALIDATE DONOR INVENTORY
    # =====================================================

    def validate_transfer(
        self,
        inventory,
        requested_quantity: int,
    ) -> bool:

        if inventory is None:
            return False

        if requested_quantity <= 0:
            return False

        if inventory.available_stock < requested_quantity:
            return False

        projected_stock = (
            inventory.available_stock
            - requested_quantity
        )

        return (
            projected_stock
            >=
            inventory.minimum_threshold
        )

    # =====================================================
    # VALIDATE FACILITY ADMIN AUTHORIZATION
    # =====================================================

    def validate_facility_admin(
        self,
        user: User,
        facility_id: UUID,
    ) -> None:

        if user is None:
            raise ValueError(
                "Authenticated user is required."
            )

        if not user.is_active:
            raise PermissionError(
                "User account is inactive."
            )

        try:
            user_role = UserRoleEnum(
                user.role
            )
        except ValueError:
            raise PermissionError(
                "User has an invalid application role."
            )

        if user_role != UserRoleEnum.HOSPITAL_ADMIN:
            raise PermissionError(
                "Only hospital administrators can "
                "approve or reject transfers."
            )

        memberships = (
            self.facility_user_repository
            .get_by_user(
                user.user_id
            )
        )

        authorized = any(
            membership.facility_id == facility_id
            and membership.assigned_role
            == UserRoleEnum.HOSPITAL_ADMIN
            for membership in memberships
        )

        if not authorized:
            raise PermissionError(
                "Hospital administrator is not authorized "
                "for the destination facility."
            )

    # =====================================================
    # CREATE TRANSFER REQUEST
    # =====================================================

    def create_transfer_request(
        self,
        transfer_data: dict,
    ):

        requested_quantity = transfer_data.get(
            "requested_quantity"
        )

        self.validate_quantity(
            requested_quantity
        )

        inventory = (
            self.inventory_repository
            .get_inventory_record(
                facility_id=transfer_data[
                    "from_facility_id"
                ],
                medicine_id=transfer_data[
                    "medicine_id"
                ],
            )
        )

        if inventory is None:

            raise ValueError(
                "Donor inventory not found."
            )

        is_safe = (
            self.validate_transfer(
                inventory,
                requested_quantity,
            )
        )

        if not is_safe:

            raise ValueError(
                "Transfer rejected. "
                "Donor facility would fall "
                "below the minimum inventory "
                "threshold."
            )

        transfer_data["cascade_safe"] = True

        try:

            transfer = (
                self.redistribution_repository
                .create_transfer_request(
                    transfer_data
                )
            )

            self.db.commit()

            self.db.refresh(
                transfer
            )

            return transfer

        except Exception:

            self.db.rollback()

            raise

    # =====================================================
    # GET TRANSFER BY ID
    # =====================================================

    def get_transfer(
        self,
        transfer_id: UUID,
    ):

        transfer = (
            self.redistribution_repository
            .get_transfer_response_by_id(
                transfer_id
            )
        )

        if transfer is None:

            raise ValueError(
                "Transfer not found."
            )

        return transfer

    # =====================================================
    # APPROVE TRANSFER
    #
    # 1. Lock transfer
    # 2. Verify PENDING
    # 3. Verify destination-facility authorization
    # 4. Lock donor inventory
    # 5. Revalidate current inventory
    # 6. Reserve inventory
    # 7. Update transfer
    # 8. Commit atomically
    # 9. Return enriched transfer response
    # =====================================================

    def approve_transfer(
        self,
        transfer_id: UUID,
        approved_quantity: int,
        approver: User,
    ):

        self.validate_quantity(
            approved_quantity
        )

        if approver is None:
            raise ValueError(
                "Approver identity is required."
            )

        try:

            transfer = (
                self.redistribution_repository
                .get_transfer_for_approval(
                    transfer_id
                )
            )

            if transfer is None:

                raise ValueError(
                    "Transfer not found."
                )

            # -----------------------------------------
            # AUTHORIZATION
            # -----------------------------------------

            self.validate_facility_admin(
                user=approver,
                facility_id=transfer.to_facility_id,
            )

            # -----------------------------------------
            # STATE VALIDATION
            # -----------------------------------------

            self.validate_transfer_transition(
                transfer.transfer_status,
                TransferStatusEnum.APPROVED,
            )

            if (
                approved_quantity
                >
                transfer.requested_quantity
            ):

                raise ValueError(
                    "Approved quantity cannot "
                    "exceed the requested quantity."
                )

            # -----------------------------------------
            # LOCK DONOR INVENTORY
            # -----------------------------------------

            inventory = (
                self.redistribution_repository
                .get_inventory_for_transfer(
                    facility_id=(
                        transfer.from_facility_id
                    ),
                    medicine_id=(
                        transfer.medicine_id
                    ),
                )
            )

            if inventory is None:

                raise ValueError(
                    "Donor inventory not found."
                )

            # -----------------------------------------
            # REVALIDATE CURRENT INVENTORY
            # -----------------------------------------

            is_safe = (
                self.validate_transfer(
                    inventory,
                    approved_quantity,
                )
            )

            if not is_safe:

                raise ValueError(
                    "Transfer cannot be approved. "
                    "Current donor inventory is "
                    "insufficient to maintain the "
                    "minimum safety threshold."
                )

            # -----------------------------------------
            # RESERVE INVENTORY
            # -----------------------------------------

            inventory.available_stock -= (
                approved_quantity
            )

            inventory.reserved_stock += (
                approved_quantity
            )

            # -----------------------------------------
            # UPDATE TRANSFER
            # -----------------------------------------

            transfer.transfer_status = (
                TransferStatusEnum.APPROVED
            )

            transfer.approved_quantity = (
                approved_quantity
            )

            transfer.approved_by = (
                approver.user_id
            )

            transfer.approved_at = (
                datetime.now(timezone.utc)
            )

            transfer.cascade_safe = True

            audit_entity_id = transfer.emergency_case_id or transfer.transfer_id
            audit_entity_type = "EMERGENCY" if transfer.emergency_case_id else "TRANSFER"
            audit_service = AuditService(self.db)
            audit_service.record_event(
                action_type="ALLOCATION_APPROVED",
                entity_type=audit_entity_type,
                entity_id=audit_entity_id,
                user_id=approver.user_id,
                new_value={"approved_quantity": approved_quantity},
            )
            audit_service.record_event(
                action_type="INVENTORY_RESERVED",
                entity_type=audit_entity_type,
                entity_id=audit_entity_id,
                user_id=approver.user_id,
                new_value={"quantity": approved_quantity},
            )

            # -----------------------------------------
            # ATOMIC COMMIT
            # -----------------------------------------

            self.db.commit()

            # -----------------------------------------
            # RETURN ENRICHED RESPONSE
            #
            # The API response schema requires:
            # - from_facility_name
            # - to_facility_name
            # - medicine_name
            #
            # Therefore, return the repository's
            # enriched response instead of the raw ORM
            # TransferRequest object.
            # -----------------------------------------

            return (
                self.redistribution_repository
                .get_transfer_response_by_id(
                    transfer_id
                )
            )

        except Exception:

            self.db.rollback()

            raise

    # =====================================================
    # REJECT TRANSFER
    #
    # No inventory is reserved.
    # =====================================================

    def reject_transfer(
        self,
        transfer_id: UUID,
        rejected_by: User,
        reason: str,
    ):

        if rejected_by is None:

            raise ValueError(
                "Rejecting user identity is required."
            )

        if not reason or not reason.strip():

            raise ValueError(
                "Rejection reason is required."
            )

        try:

            transfer = (
                self.redistribution_repository
                .get_transfer_for_approval(
                    transfer_id
                )
            )

            if transfer is None:

                raise ValueError(
                    "Transfer not found."
                )

            # -----------------------------------------
            # AUTHORIZATION
            # -----------------------------------------

            self.validate_facility_admin(
                user=rejected_by,
                facility_id=transfer.to_facility_id,
            )

            # -----------------------------------------
            # STATE VALIDATION
            # -----------------------------------------

            self.validate_transfer_transition(
                transfer.transfer_status,
                TransferStatusEnum.REJECTED,
            )

            transfer.transfer_status = (
                TransferStatusEnum.REJECTED
            )

            # The current schema/database does not
            # contain a confirmed rejection_reason field.
            #
            # Therefore the reason is validated and
            # returned to the caller but not persisted
            # until we explicitly introduce that field.

            self.db.commit()

            self.db.refresh(
                transfer
            )

            return {
                "transfer": transfer,
                "rejected_by": rejected_by.user_id,
                "reason": reason.strip(),
            }

        except Exception:

            self.db.rollback()

            raise

    # =====================================================
    # GET ALL TRANSFERS
    # =====================================================

    def get_all_transfers(self):

        return (
            self.redistribution_repository
            .get_all_transfers()
        )

    # =====================================================
    # GET HIGH PRIORITY TRANSFERS
    # =====================================================

    def get_high_priority_transfers(self):

        return (
            self.redistribution_repository
            .get_high_priority_transfers()
        )

    # =====================================================
    # GET FACILITY TRANSFERS
    # =====================================================

    def get_facility_transfers(
        self,
        facility_id: UUID,
    ):

        return (
            self.redistribution_repository
            .get_transfers_for_facility(
                facility_id
            )
        )

    # =====================================================
    # GET TRANSFERS BY STATUS
    # =====================================================

    def get_transfers_by_status(
        self,
        status: TransferStatusEnum,
    ):

        return (
            self.redistribution_repository
            .get_transfers_by_status(
                status
            )
        )

    # =====================================================
    # DASHBOARD
    # =====================================================

    def get_dashboard(self):

        return (
            self.redistribution_repository
            .get_dashboard()
        )