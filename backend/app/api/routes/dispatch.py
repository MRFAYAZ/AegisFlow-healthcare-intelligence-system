from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import UserRoleEnum
from app.api.dependencies.auth import require_roles
from app.repositories.redistribution_repository import RedistributionRepository
from app.schemas.dispatch import DispatchAssignmentRequest, DispatchResponse
from app.services.dispatch_service import DispatchService
from app.core.enums import TransferStatusEnum

router = APIRouter(
    prefix="/dispatch",
    tags=["Dispatch Operations"],
)


@router.get("/dashboard")
def get_dispatch_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            [
                UserRoleEnum.EMERGENCY_OPERATOR,
                UserRoleEnum.SYSTEM_ADMIN,
                UserRoleEnum.DISPATCHER,
            ]
        )
    ),
):
    repository = RedistributionRepository(db)
    transfers = repository.get_dispatch_queue()

    return {
        "total_active_transfers": len(transfers),
        "awaiting_dispatch": sum(
            1 for transfer in transfers
            if transfer["transfer_status"] == TransferStatusEnum.APPROVED
            and transfer["dispatch_status"] is None
        ),
        "in_transit": sum(
            1 for transfer in transfers
            if transfer["transfer_status"] == TransferStatusEnum.IN_TRANSIT
        ),
        "delivered_today": repository.get_delivered_today_count(),
        "transfers": transfers,
    }


@router.post(
    "/{transfer_id}/assign",
    response_model=DispatchResponse,
)
def assign_dispatch(
    transfer_id: UUID,
    request: DispatchAssignmentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            [UserRoleEnum.EMERGENCY_OPERATOR, UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.DISPATCHER]
        )
    ),
):
    service = DispatchService(db)

    try:
        dispatch = service.assign_dispatch(
            transfer_id=transfer_id,
            dispatcher_id=current_user.user_id,
            transport_type=request.transport_type,
            vehicle_reference=request.vehicle_reference,
        )

        db.commit()
        db.refresh(dispatch)

        return dispatch

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.post(
    "/{transfer_id}/dispatch",
    response_model=DispatchResponse,
)
def dispatch_transfer(
    transfer_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            [UserRoleEnum.EMERGENCY_OPERATOR, UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.DISPATCHER]
        )
    ),
):
    service = DispatchService(db)

    try:
        dispatch = service.dispatch_transfer(transfer_id)
        db.commit()
        db.refresh(dispatch)
        return dispatch

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.post(
    "/{transfer_id}/delivered",
    response_model=DispatchResponse,
)
def mark_delivered(
    transfer_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            [UserRoleEnum.EMERGENCY_OPERATOR, UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.DISPATCHER]
        )
    ),
):
    service = DispatchService(db)

    try:
        dispatch = service.mark_delivered(transfer_id)
        db.commit()
        db.refresh(dispatch)
        return dispatch

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
