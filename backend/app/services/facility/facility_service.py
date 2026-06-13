from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.facility import Facility

from app.repositories.facility_repository import (
    FacilityRepository
)

from app.schemas.facility import (
    FacilityCreate
)


class FacilityService:

    def __init__(self, db: Session):

        self.db = db

        self.repository = FacilityRepository(db)

    # =====================================================
    # CREATE FACILITY
    # =====================================================

    def create_facility(
        self,
        payload: FacilityCreate
    ):

        existing_license = (
            self.repository.get_by_license(
                payload.license_number
            )
        )

        if existing_license:

            raise HTTPException(
                status_code=400,
                detail="License number already exists."
            )

        existing_email = (
            self.repository.get_by_email(
                payload.contact_email
            )
        )

        if existing_email:

            raise HTTPException(
                status_code=400,
                detail="Contact email already exists."
            )

        facility = Facility(

            facility_name=payload.facility_name,

            facility_type=payload.facility_type,

            location_id=payload.location_id,

            license_number=payload.license_number,

            contact_email=payload.contact_email,

            contact_phone=payload.contact_phone,

            emergency_contact=payload.emergency_contact,

            is_24x7=payload.is_24x7
        )

        return self.repository.create(
            facility
        )

    # =====================================================
    # GET FACILITY
    # =====================================================

    def get_facility(
        self,
        facility_id: UUID
    ):

        facility = (
            self.repository.get_by_id(
                facility_id
            )
        )

        if not facility:

            raise HTTPException(
                status_code=404,
                detail="Facility not found."
            )

        return facility

    # =====================================================
    # GET ALL FACILITIES
    # =====================================================

    def get_all_facilities(self):

        return (
            self.repository
            .get_all_facilities()
        )