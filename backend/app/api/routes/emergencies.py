from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.emergency.emergency_service import (
    EmergencyService
)

from app.schemas.emergency import (
    EmergencyResponse
)

router = APIRouter(
    prefix="/emergencies",
    tags=["Emergencies"]
)


# =====================================================
# GET ALL EMERGENCIES
# =====================================================

@router.get(
    "",
    response_model=list[EmergencyResponse]
)
def get_all_emergencies(
    db: Session = Depends(get_db)
):

    service = EmergencyService(db)

    return service.get_all_emergencies()


# =====================================================
# GET ACTIVE EMERGENCIES
# =====================================================

@router.get(
    "/active",
    response_model=list[EmergencyResponse]
)
def get_active_emergencies(
    db: Session = Depends(get_db)
):

    service = EmergencyService(db)

    return service.get_active_emergencies()


# =====================================================
# GET CRITICAL EMERGENCIES
# =====================================================

@router.get(
    "/critical",
    response_model=list[EmergencyResponse]
)
def get_critical_emergencies(
    db: Session = Depends(get_db)
):

    service = EmergencyService(db)

    return service.get_critical_emergencies()


# =====================================================
# DASHBOARD
# =====================================================

@router.get(
    "/dashboard"
)
def get_dashboard(
    db: Session = Depends(get_db)
):

    service = EmergencyService(db)

    return service.get_dashboard()