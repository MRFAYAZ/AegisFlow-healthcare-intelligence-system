from sqlalchemy.orm import Session

from app.repositories.inventory_repository import (
    InventoryRepository
)

from app.services.inventory.shortage_service import (
    ShortageService
)

from app.models.inventory import (
    InventoryCurrent
)


class InventoryService:

    def __init__(self, db: Session):

        self.inventory_repository = (
            InventoryRepository(db)
        )

    # =====================================================
    # CREATE INVENTORY RECORD
    # =====================================================

    def create_inventory(
        self,
        inventory_data
    ):

        # ---------------------------------------------
        # CALCULATE SHORTAGE SCORE
        # ---------------------------------------------

        shortage_score = (
            ShortageService
            .calculate_shortage_score(
                available_stock=
                inventory_data[
                    "available_stock"
                ],

                daily_consumption_rate=
                inventory_data[
                    "daily_consumption_rate"
                ],

                lead_time_days=
                inventory_data[
                    "lead_time_days"
                ],

                safety_stock_days=7
            )
        )

        # ---------------------------------------------
        # DETERMINE SEVERITY
        # ---------------------------------------------

        severity = (
            ShortageService
            .determine_severity(
                shortage_score
            )
        )

        # ---------------------------------------------
        # ENRICH INVENTORY DATA
        # ---------------------------------------------

        inventory_data[
            "shortage_score"
        ] = shortage_score

        inventory_data[
            "severity"
        ] = severity

        # ---------------------------------------------
        # SAVE INVENTORY
        # ---------------------------------------------

        return (
            self.inventory_repository
            .create_inventory(
                inventory_data
            )
        )

    # =====================================================
    # GET LOW STOCK INVENTORY
    # =====================================================

    def get_low_stock_inventory(self):

        return (
            self.inventory_repository
            .get_low_stock_inventory()
        )
    
    # =====================================================
    # GET ALL INVENTORY
    # =====================================================

    def get_all_inventory(self):

        inventory = (
            self.inventory_repository
            .get_all_inventory()
        )

        return [
            {
                "inventory_id":
                    item.inventory_id,

                "facility_name":
                    item.facility.facility_name,

                "medicine_name":
                    item.medicine.medicine_name,

                "total_stock":
                    item.total_stock,

                "available_stock":
                    item.available_stock,

                "reserved_stock":
                    item.reserved_stock,

                "shortage_score":
                    item.shortage_score,

                "severity":
                    item.severity
            }
            for item in inventory
        ]


    # =====================================================
    # GET INVENTORY BY FACILITY
    # =====================================================

    def get_inventory_by_facility(
        self,
        facility_id
    ):

        return (
            self.inventory_repository
            .get_inventory_by_facility(
                facility_id
            )
        )


    # =====================================================
    # GET CRITICAL INVENTORY
    # =====================================================

    def get_critical_inventory(self):

        return (
            self.inventory_repository
            .get_critical_inventory()
        )


    # =====================================================
    # DASHBOARD SUMMARY
    # =====================================================

    def get_dashboard(self):

        return (
            self.inventory_repository
            .get_inventory_dashboard()
        )