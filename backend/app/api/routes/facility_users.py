from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.core.database import get_db
from app.core.enums import UserRoleEnum
from app.models.user import User
from app.services.auth.facility_user_service import FacilityUserService
from app.schemas.facility_user import FacilityUserResponse

router = APIRouter(prefix="/facility-users", tags=["Facility Users"])


@router.get("", response_model=list[FacilityUserResponse])
def get_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.SYSTEM_ADMIN])),
):
    return FacilityUserService(db).get_all()


@router.get("/facility/{facility_id}", response_model=list[FacilityUserResponse])
def get_by_facility(
    facility_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([
        UserRoleEnum.SYSTEM_ADMIN,
        UserRoleEnum.HOSPITAL_ADMIN,
        UserRoleEnum.PHARMACIST,
        UserRoleEnum.SHOP_OWNER,
        UserRoleEnum.SUPPLIER,
    ])),
):
    service = FacilityUserService(db)
    if current_user.role != UserRoleEnum.SYSTEM_ADMIN:
        own_assignments = service.get_by_user(current_user.user_id)
        if facility_id not in {assignment.facility_id for assignment in own_assignments}:
            raise HTTPException(
                status_code=403,
                detail="You may only view user assignments for your own facility.",
            )
    return service.get_by_facility(facility_id)


@router.get("/user/{user_id}", response_model=list[FacilityUserResponse])
def get_by_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([
        UserRoleEnum.SYSTEM_ADMIN,
        UserRoleEnum.HOSPITAL_ADMIN,
        UserRoleEnum.PHARMACIST,
        UserRoleEnum.SHOP_OWNER,
        UserRoleEnum.SUPPLIER,
        UserRoleEnum.EMERGENCY_OPERATOR,
    ])),
):
    if current_user.role != UserRoleEnum.SYSTEM_ADMIN and current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="You may only view your own facility memberships.")
    return FacilityUserService(db).get_by_user(user_id)
