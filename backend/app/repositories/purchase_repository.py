from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.purchase import (
    PurchaseTransaction
)

from app.repositories.base_repository import (
    BaseRepository
)


class PurchaseRepository(BaseRepository):

    def __init__(self, db: Session):
        super().__init__(db)

    # =====================================================
    # GET PURCHASES BY FACILITY
    # =====================================================

    def get_purchases_by_facility(
        self,
        facility_id
    ):

        query = (
            select(PurchaseTransaction)
            .where(
                PurchaseTransaction.facility_id
                == facility_id
            )
        )

        return self.db.execute(query).scalars().all()

    # =====================================================
    # CREATE PURCHASE
    # =====================================================

    def create_purchase(
        self,
        purchase_data
    ):

        purchase = PurchaseTransaction(
            **purchase_data
        )

        self.db.add(purchase)

        self.db.commit()

        self.db.refresh(purchase)

        return purchase