from uuid import UUID  # <-- ADDED THIS IMPORT
from fastapi import (
    APIRouter,
    Depends
)
from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import UserRoleEnum
from app.api.dependencies.auth import get_current_user, require_roles
from app.models.user import User

from app.services.allocation_service import AllocationService
from app.schemas.allocation import (
    AllocationApprovalRequest,
    AllocationApprovalResponse,
    AllocationPlanResponse,
)

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


# =====================================================
# GET EMERGENCY MATCHES
# =====================================================

@router.get(
    "/{emergency_case_id}/matches"
)
def get_matches(
    emergency_case_id: UUID,
    db: Session = Depends(get_db)  # <-- Adjusted to match your other routes
):
    
    service = EmergencyService(db)

    return service.get_matches(
        emergency_case_id
    )


@router.post("/{emergency_case_id}/allocation")
def generate_allocation(
    emergency_case_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            [
                UserRoleEnum.EMERGENCY_OPERATOR,
                UserRoleEnum.SYSTEM_ADMIN,
            ]
        )
    ),
):
    try:
        plan = AllocationService(db).generate_allocation_plan(
            emergency_case_id
        )
        db.commit()
        db.refresh(plan)
        return plan
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/{emergency_case_id}/allocation",
    response_model=AllocationPlanResponse,
)
def get_allocation(
    emergency_case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return AllocationService(db).get_authorized_allocation_plan(
            emergency_case_id=emergency_case_id,
            current_user=current_user,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
    except ValueError as exc:
        detail = str(exc)
        code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in detail.lower()
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=code, detail=detail)


@router.post(
    "/{emergency_case_id}/allocation/approve",
    response_model=AllocationApprovalResponse,
)
def approve_allocation(
    emergency_case_id: UUID,
    payload: AllocationApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRoleEnum.HOSPITAL_ADMIN])
    ),
):
    try:
        plan, transfer_ids = AllocationService(db).approve_allocation(
            emergency_case_id,
            [
                (line.allocation_line_id, line.approved_quantity)
                for line in payload.lines
            ],
            current_user,
        )
        db.commit()
        db.refresh(plan)
        return {
            "message": "Allocation approved successfully.",
            "allocation_plan_id": plan.allocation_plan_id,
            "status": plan.status,
            "allocated_quantity": plan.allocated_quantity,
            "fulfillment_percentage": plan.fulfillment_percentage,
            "transfer_ids": transfer_ids,
        }
    except PermissionError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post(
    "/{emergency_case_id}/allocation/reject",
    response_model=AllocationPlanResponse,
)
def reject_allocation(
    emergency_case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRoleEnum.HOSPITAL_ADMIN])
    ),
):
    try:
        plan = AllocationService(db).reject_allocation(
            emergency_case_id,
            current_user,
        )
        db.commit()
        db.refresh(plan)
        return plan
    except PermissionError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))