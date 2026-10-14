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

    def get_shortage_risk_assessments(self):
        assessments = []
        for item in self.inventory_repository.get_all_inventory():
            current_stock = max(int(item.total_stock or 0), 0)
            reserved_stock = max(int(item.reserved_stock or 0), 0)
            usable_stock = max(current_stock - reserved_stock, 0)
            daily_consumption = max(float(item.daily_consumption_rate or 0), 0)
            safety_stock_days = max(int(item.medicine.safety_stock_days or 0), 0)
            lead_time_days = max(
                int(item.lead_time_days or 0),
                int(item.medicine.standard_lead_time_days or 0),
            )
            safety_stock_units = daily_consumption * safety_stock_days

            if daily_consumption == 0:
                projected_days = None
                risk_score = 0.0
                risk_level = "SAFE"
            else:
                projected_days = round(usable_stock / daily_consumption, 2)
                planning_horizon = max(lead_time_days + safety_stock_days, 1)
                risk_score = round(
                    min(100.0, max(0.0, (1 - projected_days / planning_horizon) * 100)),
                    1,
                )
                if projected_days <= lead_time_days:
                    risk_level = "CRITICAL"
                elif projected_days <= lead_time_days + safety_stock_days:
                    risk_level = "HIGH"
                elif projected_days <= lead_time_days + (safety_stock_days * 2):
                    risk_level = "WARNING"
                else:
                    risk_level = "SAFE"

            recommended_action = {
                "SAFE": "CONTINUE_MONITORING",
                "WARNING": "PREPARE_REPLENISHMENT",
                "HIGH": "INITIATE_PROCUREMENT",
                "CRITICAL": "SOURCE_NETWORK",
            }[risk_level]

            assessments.append({
                "inventory_id": item.inventory_id,
                "facility_id": item.facility_id,
                "medicine_id": item.medicine_id,
                "facility_name": item.facility.facility_name,
                "medicine_name": item.medicine.medicine_name,
                "current_stock": current_stock,
                "reserved_stock": reserved_stock,
                "usable_stock": usable_stock,
                "daily_consumption": round(daily_consumption, 2),
                "safety_stock_days": safety_stock_days,
                "safety_stock_units": round(safety_stock_units, 2),
                "lead_time_days": lead_time_days,
                "projected_stockout_days": projected_days,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "recommended_action": recommended_action,
            })

        return sorted(
            assessments,
            key=lambda assessment: (
                {"CRITICAL": 0, "HIGH": 1, "WARNING": 2, "SAFE": 3}[assessment["risk_level"]],
                assessment["projected_stockout_days"] if assessment["projected_stockout_days"] is not None else float("inf"),
            ),
        )