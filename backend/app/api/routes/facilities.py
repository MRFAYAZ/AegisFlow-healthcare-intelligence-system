from uuid import UUID

from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.facility.facility_service import (
    FacilityService
)

from app.schemas.facility import (
    FacilityCreate,
    FacilityResponse
)


router = APIRouter(
    prefix="/facilities",
    tags=["Facilities"]
)


# =====================================================
# CREATE FACILITY
# =====================================================

@router.post(
    "",
    response_model=FacilityResponse
)
def create_facility(
    payload: FacilityCreate,
    db: Session = Depends(get_db)
):

    service = FacilityService(db)

    return service.create_facility(
        payload
    )


# =====================================================
# GET ALL FACILITIES
# =====================================================

@router.get(
    "",
    response_model=list[FacilityResponse]
)
def get_all_facilities(
    db: Session = Depends(get_db)
):

    service = FacilityService(db)

    return service.get_all_facilities()


# =====================================================
# GET FACILITY BY ID
# =====================================================

@router.get(
    "/{facility_id}",
    response_model=FacilityResponse
)
def get_facility(
    facility_id: UUID,
    db: Session = Depends(get_db)
):

    service = FacilityService(db)

    return service.get_facility(
        facility_id
    )