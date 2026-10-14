from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies.auth import require_roles
from app.core.enums import UserRoleEnum
from app.models.user import User
from app.schemas.emergency import EmergencyResponse
from app.schemas.match import EmergencyMatchResponse
from app.services.emergency.emergency_service import EmergencyService

router = APIRouter(prefix="/emergencies", tags=["Emergencies"])


@router.get("", response_model=list[EmergencyResponse])
def get_all_emergencies(db: Session = Depends(get_db)):
    return EmergencyService(db).get_all_emergencies()


@router.get("/active", response_model=list[EmergencyResponse])
def get_active_emergencies(db: Session = Depends(get_db)):
    return EmergencyService(db).get_active_emergencies()


@router.get("/critical", response_model=list[EmergencyResponse])
def get_critical_emergencies(db: Session = Depends(get_db)):
    return EmergencyService(db).get_critical_emergencies()


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    return EmergencyService(db).get_dashboard()


@router.get(
    "/{emergency_case_id}/timeline",
    summary="Return persisted emergency, transfer and dispatch milestones",
)
def get_emergency_timeline(
    emergency_case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([
            UserRoleEnum.SYSTEM_ADMIN,
            UserRoleEnum.EMERGENCY_OPERATOR,
            UserRoleEnum.HOSPITAL_ADMIN,
        ])
    ),
):
    try:
        return EmergencyService(db).get_timeline_for_emergency(
            emergency_case_id=emergency_case_id,
            user=current_user,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/{emergency_case_id}/matches",
    response_model=list[EmergencyMatchResponse],
    summary="Rank eligible donor facilities for an emergency",
    description=(
        "Returns safe transferable quantities, straight-line geographic distance, "
        "weighted match scores and an explanation for each recommendation. Distance "
        "is not a road route or guaranteed travel-time estimate."
    ),
)
def get_emergency_matches(
    emergency_case_id: UUID,
    max_distance_km: float | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([
            UserRoleEnum.SYSTEM_ADMIN,
            UserRoleEnum.EMERGENCY_OPERATOR,
            UserRoleEnum.HOSPITAL_ADMIN,
        ])
    ),
):
    try:
        return EmergencyService(db).get_matches_for_emergency(
            emergency_case_id=emergency_case_id,
            max_distance_km=max_distance_km,
            user=current_user,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
