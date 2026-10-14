from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.core.database import get_db
from app.core.enums import UserRoleEnum
from app.models.user import User
from app.services.alerts.alert_service import AlertService
from app.schemas.alert import AlertResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])
ALERT_READ_ROLES = [
    UserRoleEnum.SYSTEM_ADMIN,
    UserRoleEnum.EMERGENCY_OPERATOR,
    UserRoleEnum.HOSPITAL_ADMIN,
    UserRoleEnum.PHARMACIST,
    UserRoleEnum.SHOP_OWNER,
    UserRoleEnum.SUPPLIER,
]


def _service_call(callable_):
    try:
        return callable_()
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("", response_model=list[AlertResponse])
def get_all_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ALERT_READ_ROLES)),
):
    service = AlertService(db)
    return _service_call(lambda: service.get_all_alerts_for_user(current_user))


@router.get("/active", response_model=list[AlertResponse])
def get_active_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ALERT_READ_ROLES)),
):
    service = AlertService(db)
    return _service_call(lambda: service.get_active_alerts_for_user(current_user))


@router.get("/critical", response_model=list[AlertResponse])
def get_critical_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ALERT_READ_ROLES)),
):
    service = AlertService(db)
    return _service_call(lambda: service.get_critical_alerts_for_user(current_user))


@router.get("/dashboard")
def get_alert_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(ALERT_READ_ROLES)),
):
    service = AlertService(db)
    return _service_call(lambda: service.get_dashboard_for_user(current_user))
