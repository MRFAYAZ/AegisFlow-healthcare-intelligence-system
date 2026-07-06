from sqlalchemy.orm import Session

from app.core.enums import TransferStatusEnum
from app.models.redistribution import TransferRequest
from app.repositories.inventory_repository import (
    InventoryRepository
)

from app.repositories.emergency_repository import EmergencyRepository

from app.repositories.redistribution_repository import (
    RedistributionRepository
)


class RedistributionService:

    def __init__(self, db: Session):

        self.db = db

        self.inventory_repository = (
            InventoryRepository(db)
        )

        self.redistribution_repository = (
            RedistributionRepository(db)
        )

        self.emergency_repository = (
            EmergencyRepository(db)
        )

    # =====================================================
    # VALIDATE DONOR FACILITY
    # =====================================================

    def validate_transfer(
        self,
        inventory,
        requested_quantity
    ):

        projected_stock = (

            inventory.available_stock

            -

            requested_quantity

        )

        return (

            projected_stock
            >=
            inventory.minimum_threshold

        )

    # =====================================================
    # CREATE TRANSFER
    # =====================================================

    def create_transfer_request(
        self,
        transfer_data
    ):

        inventory = (
            self.inventory_repository
            .get_inventory_record(
                facility_id=
                transfer_data[
                    "from_facility_id"
                ],

                medicine_id=
                transfer_data[
                    "medicine_id"
                ]
            )
        )

        if not inventory:

            raise ValueError(
                "Inventory not found."
            )

        is_safe = (
            self.validate_transfer(
                inventory,
                transfer_data[
                    "requested_quantity"
                ]
            )
        )

        if not is_safe:

            raise ValueError(
                "Transfer rejected. "
                "Donor facility would "
                "fall below threshold."
            )

        transfer_data[
            "cascade_safe"
        ] = True

        return (

            self.redistribution_repository
            .create_transfer_request(
                transfer_data
            )

        )
    
    # =====================================================
    # GET ALL TRANSFERS
    # =====================================================

    def get_all_transfers(self):

        return (
            self.redistribution_repository
            .get_all_transfers()
        )


    # =====================================================
    # GET HIGH PRIORITY
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
        facility_id
    ):

        return (
            self.redistribution_repository
            .get_transfers_for_facility(
                facility_id
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

    def dispatch_transfer(self, emergency_case_id):
        emergency = self.emergency_repository.get_all_emergencies()
        matching_emergency = next(
            (item for item in emergency if str(item["emergency_case_id"]) == str(emergency_case_id)),
            None,
        )

        if not matching_emergency:
            raise ValueError("Emergency not found.")

        transfer_id = matching_emergency.get("transfer_id")
        if not transfer_id:
            raise ValueError("No transfer recommendation available.")

        transfer = self.db.get(TransferRequest, transfer_id)
        if transfer is None:
            raise ValueError("Transfer not found.")

        transfer.transfer_status = TransferStatusEnum.PENDING
        transfer.recommendation_reason = matching_emergency.get("recommendation_reason") or "Highest inventory with minimum delivery distance."
        transfer.match_score = matching_emergency.get("match_score")
        transfer.transfer_distance_km = matching_emergency.get("transfer_distance_km")
        transfer.cascade_safe = matching_emergency.get("cascade_safe")
        self.db.commit()
        self.db.refresh(transfer)

        return {
            "emergency_case_id": emergency_case_id,
            "transfer_id": str(transfer_id),
            "transfer_status": transfer.transfer_status.value,
            "message": "Dispatch request confirmed. Donor hospital has been notified.",
        }