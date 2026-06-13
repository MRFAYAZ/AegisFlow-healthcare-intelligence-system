from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.facility import Facility

from app.repositories.base_repository import (
    BaseRepository
)


class FacilityRepository(BaseRepository):

    def __init__(self, db: Session):
        super().__init__(db)

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        facility: Facility
    ):

        self.db.add(facility)

        self.db.commit()

        self.db.refresh(facility)

        return facility


    # =====================================================
    # GET BY LICENSE
    # =====================================================

    def get_by_license(
        self,
        license_number: str
    ):

        query = (
            select(Facility)
            .where(
                Facility.license_number
                ==
                license_number
            )
        )

        return (
            self.db.execute(query)
            .scalar_one_or_none()
        )


    # =====================================================
    # GET BY EMAIL
    # =====================================================

    def get_by_email(
        self,
        email: str
    ):

        query = (
            select(Facility)
            .where(
                Facility.contact_email
                ==
                email
            )
        )

        return (
            self.db.execute(query)
            .scalar_one_or_none()
        )

    # =====================================================
    # GET FACILITY BY ID
    # =====================================================

    def get_by_id(self, facility_id):

        query = (
            select(Facility)
            .where(
                Facility.facility_id == facility_id
            )
        )

        return self.db.execute(query).scalar_one_or_none()

    # =====================================================
    # GET ALL FACILITIES
    # =====================================================

    def get_all_facilities(self):

        query = select(Facility)

        return self.db.execute(query).scalars().all()