from uuid import UUID

from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.auth.facility_user_service import (
    FacilityUserService
)

from app.schemas.facility_user import (
    FacilityUserResponse
)

router = APIRouter(
    prefix="/facility-users",
    tags=["Facility Users"]
)


@router.get(
    "",
    response_model=list[
        FacilityUserResponse
    ]
)
def get_all(
    db: Session = Depends(get_db)
):

    return (
        FacilityUserService(db)
        .get_all()
    )


@router.get(
    "/facility/{facility_id}",
    response_model=list[
        FacilityUserResponse
    ]
)
def get_by_facility(
    facility_id: UUID,
    db: Session = Depends(get_db)
):

    return (
        FacilityUserService(db)
        .get_by_facility(
            facility_id
        )
    )


@router.get(
    "/user/{user_id}",
    response_model=list[
        FacilityUserResponse
    ]
)
def get_by_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):

    return (
        FacilityUserService(db)
        .get_by_user(
            user_id
        )
    )