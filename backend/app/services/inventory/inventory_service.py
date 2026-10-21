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
from app.core.enums import SeverityEnum, UserRoleEnum
from app.models.facility_user import FacilityUser
from sqlalchemy import select


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

    def get_all_inventory(self, user=None):

        inventory = (
            self.inventory_repository
            .get_all_inventory()
        )

        if user is not None:
            if user.role in {UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR}:
                pass
            elif user.role in {
                UserRoleEnum.HOSPITAL_ADMIN,
                UserRoleEnum.PHARMACIST,
                UserRoleEnum.SHOP_OWNER,
                UserRoleEnum.SUPPLIER,
            }:
                facility_ids = self.inventory_repository.db.execute(
                    select(FacilityUser.facility_id).where(
                        FacilityUser.user_id == user.user_id
                    )
                ).scalars().all()
                if not facility_ids:
                    raise PermissionError("No facility is assigned to this user.")
                inventory = [
                    item for item in inventory
                    if item.facility_id in set(facility_ids)
                ]
            else:
                raise PermissionError("This role cannot access inventory records.")

        return [
            {
                "inventory_id": item.inventory_id,
                "facility_id": item.facility_id,
                "medicine_id": item.medicine_id,
                "facility_name": item.facility.facility_name,
                "medicine_name": item.medicine.medicine_name,
                "total_stock": item.total_stock,
                "available_stock": item.available_stock,
                "reserved_stock": item.reserved_stock,
                "shortage_score": item.shortage_score,
                "severity": item.severity,
            }
            for item in inventory
        ]


    def get_inventory_by_facility_for_user(self, facility_id, user):
        from app.core.enums import UserRoleEnum
        from sqlalchemy import select

        if user.role in {UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR}:
            return self.get_inventory_by_facility(facility_id)

        membership = self.inventory_repository.db.execute(
            select(FacilityUser.facility_user_id).where(
                FacilityUser.user_id == user.user_id,
                FacilityUser.facility_id == facility_id,
            )
        ).scalar_one_or_none()
        if membership is None:
            raise PermissionError("This facility is not assigned to the current user.")
        return self.get_inventory_by_facility(facility_id)

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

    def get_critical_inventory(self, user=None):
        if user is not None:
            inventory = self.get_all_inventory(user)
            return [
                row for row in inventory
                if row["severity"] in {SeverityEnum.CRITICAL, SeverityEnum.EMERGENCY}
            ]
        return self.inventory_repository.get_critical_inventory()


    # =====================================================
    # DASHBOARD SUMMARY
    # =====================================================

    def get_dashboard(self, user=None):
        if user is not None:
            inventory = self.get_all_inventory(user)
            return {
                "total_inventory_records": len(inventory),
                "safe": sum(row["severity"] == SeverityEnum.SAFE for row in inventory),
                "warning": sum(row["severity"] == SeverityEnum.WARNING for row in inventory),
                "critical": sum(row["severity"] == SeverityEnum.CRITICAL for row in inventory),
                "emergency": sum(row["severity"] == SeverityEnum.EMERGENCY for row in inventory),
            }
        return self.inventory_repository.get_inventory_dashboard()