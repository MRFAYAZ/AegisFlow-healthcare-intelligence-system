from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.alerts.alert_service import (
    AlertService
)

from app.schemas.alert import (
    AlertResponse
)

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


# =====================================================
# GET ALL ALERTS
# =====================================================

@router.get(
    "",
    response_model=list[AlertResponse]
)
def get_all_alerts(
    db: Session = Depends(get_db)
):

    service = AlertService(db)

    return service.get_all_alerts()


# =====================================================
# GET ACTIVE ALERTS
# =====================================================

@router.get(
    "/active",
    response_model=list[AlertResponse]
)
def get_active_alerts(
    db: Session = Depends(get_db)
):

    service = AlertService(db)

    return service.get_active_alerts()


# =====================================================
# GET CRITICAL ALERTS
# =====================================================

@router.get(
    "/critical",
    response_model=list[AlertResponse]
)
def get_critical_alerts(
    db: Session = Depends(get_db)
):

    service = AlertService(db)

    return service.get_critical_alerts()


# =====================================================
# ALERT DASHBOARD
# =====================================================

@router.get(
    "/dashboard"
)
def get_alert_dashboard(
    db: Session = Depends(get_db)
):

    service = AlertService(db)

    return service.get_dashboard()