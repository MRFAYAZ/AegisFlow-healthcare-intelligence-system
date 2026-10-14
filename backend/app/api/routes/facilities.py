from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.core.database import get_db
from app.core.enums import UserRoleEnum
from app.models.user import User
from app.services.facility.facility_service import FacilityService
from app.schemas.facility import (
    FacilityCreate,
    FacilityUpdate,
    FacilityResponse,
    FacilityNetworkResponse,
)

router = APIRouter(prefix="/facilities", tags=["Facilities"])
NETWORK_ROLES = [
    UserRoleEnum.SYSTEM_ADMIN,
    UserRoleEnum.EMERGENCY_OPERATOR,
    UserRoleEnum.HOSPITAL_ADMIN,
    UserRoleEnum.PHARMACIST,
    UserRoleEnum.SHOP_OWNER,
    UserRoleEnum.SUPPLIER,
]


@router.post("", response_model=FacilityResponse)
def create_facility(
    payload: FacilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.SYSTEM_ADMIN])),
):
    return FacilityService(db).create_facility(payload)


@router.get("", response_model=list[FacilityNetworkResponse])
def get_all_facilities(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(NETWORK_ROLES)),
):
    return FacilityService(db).get_all_facilities()


@router.get("/{facility_id}", response_model=FacilityNetworkResponse)
def get_facility(
    facility_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(NETWORK_ROLES)),
):
    return FacilityService(db).get_facility(facility_id)


@router.patch("/{facility_id}", response_model=FacilityResponse)
def update_facility(
    facility_id: UUID,
    payload: FacilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.SYSTEM_ADMIN])),
):
    return FacilityService(db).update_facility(facility_id, payload)
