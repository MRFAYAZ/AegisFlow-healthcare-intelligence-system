from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.inventory import InventoryCurrent
from app.core.enums import SeverityEnum

from app.repositories.base_repository import (
    BaseRepository
)


class InventoryRepository(BaseRepository):

    def __init__(self, db: Session):
        super().__init__(db)

    # =====================================================
    # GET INVENTORY BY FACILITY
    # =====================================================

    def get_inventory_by_facility(
        self,
        facility_id
    ):

        query = (
            select(InventoryCurrent)
            .where(
                InventoryCurrent.facility_id == facility_id
            )
        )

        return self.db.execute(query).scalars().all()

    # =====================================================
    # GET LOW STOCK INVENTORY
    # =====================================================

    def get_low_stock_inventory(self):

        query = (
            select(InventoryCurrent)
            .where(
                InventoryCurrent.severity.in_([
                    SeverityEnum.WARNING,
                    SeverityEnum.CRITICAL,
                    SeverityEnum.EMERGENCY
                ])
            )
        )

        return self.db.execute(query).scalars().all()

    # =====================================================
    # GET INVENTORY BY MEDICINE
    # =====================================================

    def get_inventory_by_medicine(
        self,
        medicine_id
    ):

        query = (
            select(InventoryCurrent)
            .where(
                InventoryCurrent.medicine_id == medicine_id
            )
        )

        return self.db.execute(query).scalars().all()

    # =====================================================
    # CREATE INVENTORY RECORD
    # =====================================================

    def create_inventory(
        self,
        inventory_data
    ):

        inventory = InventoryCurrent(**inventory_data)

        self.db.add(inventory)

        self.db.commit()

        self.db.refresh(inventory)

        return inventory
    # =====================================================
    # GET ALL INVENTORY
    # =====================================================

    def get_all_inventory(self):

        query = (
            select(InventoryCurrent)
            .options(
                joinedload(
                    InventoryCurrent.medicine
                ),
                joinedload(
                    InventoryCurrent.facility
                )
            )
        )

        return (
            self.db.execute(query)
            .scalars()
            .all()
        )


    # =====================================================
    # GET CRITICAL INVENTORY
    # =====================================================

    def get_critical_inventory(self):

        query = (
            select(InventoryCurrent)
            .where(
                InventoryCurrent.severity.in_(
                    [
                        SeverityEnum.CRITICAL,
                        SeverityEnum.EMERGENCY
                    ]
                )
            )
        )

        return (
            self.db.execute(query)
            .scalars()
            .all()
        )


    # =====================================================
    # DASHBOARD COUNTS
    # =====================================================

    def get_inventory_dashboard(self):

        inventory = self.get_all_inventory()

        return {
            "total_inventory_records": len(inventory),

            "safe": len(
                [
                    x for x in inventory
                    if x.severity == SeverityEnum.SAFE
                ]
            ),

            "warning": len(
                [
                    x for x in inventory
                    if x.severity == SeverityEnum.WARNING
                ]
            ),

            "critical": len(
                [
                    x for x in inventory
                    if x.severity == SeverityEnum.CRITICAL
                ]
            ),

            "emergency": len(
                [
                    x for x in inventory
                    if x.severity == SeverityEnum.EMERGENCY
                ]
            )
        }