from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import UserRoleEnum
from app.models.user import User

from app.api.dependencies.auth import (
    get_current_user,
    require_roles
)

from app.services.redistribution.redistribution_service import (
    RedistributionService,
)
from app.services.dispatch_service import DispatchService

from app.schemas.redistribution import (
    TransferApprovalRequest,
    TransferDispatchAssignmentRequest,
    TransferRejectionRequest,
    TransferResponse,
)


router = APIRouter(
    prefix="/redistribution",
    tags=["Redistribution"]
)


# ============================================================
# GET ALL TRANSFERS
# ============================================================

@router.get(
    "",
    response_model=list[TransferResponse]
)
def get_all_transfers(
    db: Session = Depends(get_db)
):
    service = RedistributionService(db)

    return service.get_all_transfers()


# ============================================================
# GET HIGH PRIORITY TRANSFERS
# ============================================================

@router.get(
    "/high-priority",
    response_model=list[TransferResponse]
)
def get_high_priority(
    db: Session = Depends(get_db)
):
    service = RedistributionService(db)

    return service.get_high_priority_transfers()


# ============================================================
# GET FACILITY TRANSFERS
# ============================================================

@router.get(
    "/facility/{facility_id}",
    response_model=list[TransferResponse]
)
def get_facility_transfers(
    facility_id: UUID,
    db: Session = Depends(get_db)
):
    service = RedistributionService(db)

    return service.get_facility_transfers(
        facility_id
    )


# ============================================================
# GET REDISTRIBUTION DASHBOARD
# ============================================================

@router.get(
    "/dashboard"
)
def get_dashboard(
    db: Session = Depends(get_db)
):
    service = RedistributionService(db)

    return service.get_dashboard()


# ============================================================
# GET SINGLE TRANSFER
# ============================================================

@router.get(
    "/{transfer_id}",
    response_model=TransferResponse
)
def get_transfer(
    transfer_id: UUID,
    db: Session = Depends(get_db)
):
    service = RedistributionService(db)

    try:

        return service.get_transfer(
            transfer_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )


# ============================================================
# APPROVE TRANSFER
# ============================================================

@router.post(
    "/{transfer_id}/approve",
    response_model=TransferResponse,
    status_code=status.HTTP_200_OK
)
def approve_transfer(
    transfer_id: UUID,
    payload: TransferApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRoleEnum.HOSPITAL_ADMIN]
        )
    )
):

    service = RedistributionService(db)

    try:

        return service.approve_transfer(
            transfer_id=transfer_id,
            approved_quantity=payload.approved_quantity,
            approver=current_user
        )

    except PermissionError as exc:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc)
        )

    except ValueError as exc:

        message = str(exc)

        if (
            "not found" in message.lower()
        ):
            status_code = status.HTTP_404_NOT_FOUND

        elif (
            "not pending" in message.lower()
            or "insufficient" in message.lower()
            or "inventory" in message.lower()
            or "quantity" in message.lower()
        ):
            status_code = status.HTTP_409_CONFLICT

        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=message
        )


# ============================================================
# ASSIGN DISPATCH
# ============================================================

@router.post(
    "/{transfer_id}/dispatch/assign",
    status_code=status.HTTP_200_OK,
)
def assign_dispatch(
    transfer_id: UUID,
    payload: TransferDispatchAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRoleEnum.EMERGENCY_OPERATOR, UserRoleEnum.SYSTEM_ADMIN]
        )
    ),
):
    service = DispatchService(db)

    try:
        dispatch = service.assign_dispatch(
            transfer_id=transfer_id,
            dispatcher_id=current_user.user_id,
            transport_type=payload.transport_type,
            vehicle_reference=payload.vehicle_reference,
        )
        return {
            "dispatch_id": str(dispatch.dispatch_id),
            "transfer_id": str(dispatch.transfer_id),
            "dispatcher_id": str(dispatch.dispatcher_id),
            "status": dispatch.status.value,
            "transport_type": dispatch.transport_type,
            "vehicle_reference": dispatch.vehicle_reference,
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ============================================================
# START DISPATCH
# ============================================================

@router.post(
    "/{transfer_id}/dispatch",
    status_code=status.HTTP_200_OK,
)
def dispatch_transfer(
    transfer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRoleEnum.EMERGENCY_OPERATOR, UserRoleEnum.SYSTEM_ADMIN]
        )
    ),
):
    service = DispatchService(db)

    try:
        dispatch = service.dispatch_transfer(transfer_id=transfer_id)
        return {
            "dispatch_id": str(dispatch.dispatch_id),
            "transfer_id": str(dispatch.transfer_id),
            "status": dispatch.status.value,
            "dispatched_at": dispatch.dispatched_at,
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ============================================================
# MARK DELIVERED
# ============================================================

@router.post(
    "/{transfer_id}/dispatch/delivered",
    status_code=status.HTTP_200_OK,
)
def mark_delivered(
    transfer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRoleEnum.EMERGENCY_OPERATOR, UserRoleEnum.SYSTEM_ADMIN]
        )
    ),
):
    service = DispatchService(db)

    try:
        dispatch = service.mark_delivered(transfer_id=transfer_id)
        return {
            "dispatch_id": str(dispatch.dispatch_id),
            "transfer_id": str(dispatch.transfer_id),
            "status": dispatch.status.value,
            "delivered_at": dispatch.delivered_at,
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ============================================================
# GET DISPATCH STATUS
# ============================================================

@router.get(
    "/{transfer_id}/dispatch",
    status_code=status.HTTP_200_OK,
)
def get_dispatch_status(
    transfer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRoleEnum.EMERGENCY_OPERATOR, UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.HOSPITAL_ADMIN]
        )
    ),
):
    dispatch = (
        db.query(__import__('app.models.dispatch', fromlist=['TransferDispatch']).TransferDispatch)
        .filter(__import__('app.models.dispatch', fromlist=['TransferDispatch']).TransferDispatch.transfer_id == transfer_id)
        .first()
    )

    if dispatch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch record not found.",
        )

    return {
        "dispatch_id": str(dispatch.dispatch_id),
        "transfer_id": str(dispatch.transfer_id),
        "dispatcher_id": str(dispatch.dispatcher_id) if dispatch.dispatcher_id else None,
        "transport_type": dispatch.transport_type,
        "vehicle_reference": dispatch.vehicle_reference,
        "status": dispatch.status.value,
        "dispatched_at": dispatch.dispatched_at,
        "estimated_arrival_at": dispatch.estimated_arrival_at,
        "delivered_at": dispatch.delivered_at,
    }


# ============================================================
# REJECT TRANSFER
# ============================================================

@router.post(
    "/{transfer_id}/reject",
    status_code=status.HTTP_200_OK
)
def reject_transfer(
    transfer_id: UUID,
    payload: TransferRejectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRoleEnum.HOSPITAL_ADMIN]
        )
    )
):

    service = RedistributionService(db)

    try:

        return service.reject_transfer(
            transfer_id=transfer_id,
            rejected_by=current_user,
            reason=payload.reason
        )

    except PermissionError as exc:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc)
        )

    except ValueError as exc:

        message = str(exc)

        if (
            "not found" in message.lower()
        ):
            status_code = status.HTTP_404_NOT_FOUND

        elif (
            "not pending" in message.lower()
        ):
            status_code = status.HTTP_409_CONFLICT

        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=message
        )