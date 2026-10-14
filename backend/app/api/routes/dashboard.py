from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.core.database import get_db
from app.core.enums import UserRoleEnum
from app.models.user import User
from app.services.analytics.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
DASHBOARD_ROLES = [
    UserRoleEnum.SYSTEM_ADMIN,
    UserRoleEnum.EMERGENCY_OPERATOR,
    UserRoleEnum.HOSPITAL_ADMIN,
    UserRoleEnum.PHARMACIST,
    UserRoleEnum.SHOP_OWNER,
    UserRoleEnum.SUPPLIER,
]


@router.get("/snapshot")
def get_dashboard_snapshot(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(DASHBOARD_ROLES)),
):
    try:
        return DashboardService(db).get_dashboard_snapshot_for_user(current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/review")
def get_review_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(DASHBOARD_ROLES)),
):
    try:
        return DashboardService(db).get_dashboard_for_user(current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
