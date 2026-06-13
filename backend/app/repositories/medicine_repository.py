from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.medicine import Medicine

from app.repositories.base_repository import (
    BaseRepository
)


class MedicineRepository(BaseRepository):

    def __init__(
        self,
        db: Session
    ):
        super().__init__(db)

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        medicine: Medicine
    ):

        self.db.add(medicine)

        self.db.commit()

        self.db.refresh(medicine)

        return medicine

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        medicine_id: UUID
    ):

        query = (

            select(Medicine)

            .where(
                Medicine.medicine_id
                ==
                medicine_id
            )

        )

        return (
            self.db.execute(query)
            .scalar_one_or_none()
        )

    # =====================================================
    # GET BY CODE
    # =====================================================

    def get_by_code(
        self,
        medicine_code: str
    ):

        query = (

            select(Medicine)

            .where(
                Medicine.medicine_code
                ==
                medicine_code
            )

        )

        return (
            self.db.execute(query)
            .scalar_one_or_none()
        )

    # =====================================================
    # GET ALL
    # =====================================================

    def get_all_medicines(
        self
    ):

        query = select(Medicine)

        return (
            self.db.execute(query)
            .scalars()
            .all()
        )

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        medicine: Medicine
    ):

        self.db.delete(medicine)

        self.db.commit()