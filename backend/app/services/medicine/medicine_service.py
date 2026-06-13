from uuid import UUID

from app.models.medicine import Medicine

from app.repositories.medicine_repository import (
    MedicineRepository
)


class MedicineService:

    def __init__(
        self,
        medicine_repository
    ):

        self.repository = (
            medicine_repository
        )

    # =====================================================
    # CREATE
    # =====================================================

    def create_medicine(
        self,
        data
    ):

        existing = (

            self.repository
            .get_by_code(
                data.medicine_code
            )

        )

        if existing:

            raise ValueError(
                "Medicine code already exists."
            )

        medicine = Medicine(
            **data.model_dump()
        )

        return (
            self.repository
            .create(medicine)
        )

    # =====================================================
    # GET
    # =====================================================

    def get_medicine(
        self,
        medicine_id: UUID
    ):

        medicine = (

            self.repository
            .get_by_id(
                medicine_id
            )

        )

        if not medicine:

            raise ValueError(
                "Medicine not found."
            )

        return medicine

    # =====================================================
    # GET ALL
    # =====================================================

    def get_all_medicines(
        self
    ):

        return (
            self.repository
            .get_all_medicines()
        )

    # =====================================================
    # DELETE
    # =====================================================

    def delete_medicine(
        self,
        medicine_id: UUID
    ):

        medicine = (
            self.get_medicine(
                medicine_id
            )
        )

        self.repository.delete(
            medicine
        )