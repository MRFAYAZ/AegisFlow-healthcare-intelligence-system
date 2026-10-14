from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user, require_roles
from app.core.database import get_db
from app.core.enums import UserRoleEnum
from app.models.user import User
from app.schemas.redistribution import (
    DispatchAssignmentRequest,
    TransferApprovalRequest,
    TransferRejectionRequest,
    TransferResponse,
)
from app.services.redistribution.redistribution_service import RedistributionService

router = APIRouter(prefix="/redistribution", tags=["Redistribution"])


def _raise_service_error(exc: Exception) -> None:
    if isinstance(exc, PermissionError):
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    raise exc


class DispatchRequestPayload:
    """Compatibility marker for the legacy request body."""


from pydantic import BaseModel


class EmergencyTransferRequest(BaseModel):
    emergency_case_id: UUID


@router.get("", response_model=list[TransferResponse])
def get_all_transfers(db: Session = Depends(get_db)):
    return RedistributionService(db).get_all_transfers()


@router.get("/high-priority", response_model=list[TransferResponse])
def get_high_priority(db: Session = Depends(get_db)):
    return RedistributionService(db).get_high_priority_transfers()


@router.get("/facility/{facility_id}", response_model=list[TransferResponse])
def get_facility_transfers(facility_id: UUID, db: Session = Depends(get_db)):
    return RedistributionService(db).get_facility_transfers(facility_id)


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    return RedistributionService(db).get_dashboard()


@router.post("/request", status_code=201)
def request_transfer(
    payload: EmergencyTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [
                UserRoleEnum.SYSTEM_ADMIN,
                UserRoleEnum.HOSPITAL_ADMIN,
                UserRoleEnum.EMERGENCY_OPERATOR,
            ]
        )
    ),
):
    try:
        return RedistributionService(db).request_transfer_from_emergency(
            payload.emergency_case_id, current_user
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_service_error(exc)


@router.post(
    "/dispatch",
    deprecated=True,
    status_code=201,
    summary="Compatibility alias for requesting transfer recommendations",
)
def legacy_dispatch_request(
    payload: EmergencyTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [
                UserRoleEnum.SYSTEM_ADMIN,
                UserRoleEnum.HOSPITAL_ADMIN,
                UserRoleEnum.EMERGENCY_OPERATOR,
            ]
        )
    ),
):
    # Preserve the existing request shape for older clients, but never claim
    # that a shipment has been dispatched by merely generating recommendations.
    return request_transfer(payload, db, current_user)


@router.post("/{transfer_id}/approve")
def approve_transfer(
    transfer_id: UUID,
    payload: TransferApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.HOSPITAL_ADMIN])
    ),
):
    try:
        return RedistributionService(db).approve_transfer(
            transfer_id, payload.approved_quantity, current_user
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_service_error(exc)


@router.post("/{transfer_id}/reject")
def reject_transfer(
    transfer_id: UUID,
    payload: TransferRejectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.HOSPITAL_ADMIN])
    ),
):
    try:
        return RedistributionService(db).reject_transfer(
            transfer_id, payload.reason, current_user
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_service_error(exc)


@router.post("/{transfer_id}/assign")
def assign_dispatch(
    transfer_id: UUID,
    payload: DispatchAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR])
    ),
):
    try:
        return RedistributionService(db).assign_dispatch(
            transfer_id,
            payload.transport_type,
            payload.vehicle_reference,
            current_user,
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_service_error(exc)


@router.post("/{transfer_id}/dispatch")
def dispatch_approved_transfer(
    transfer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR])
    ),
):
    try:
        return RedistributionService(db).dispatch_transfer_by_id(
            transfer_id, current_user
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_service_error(exc)


@router.post("/{transfer_id}/delivered")
def mark_transfer_delivered(
    transfer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR])
    ),
):
    try:
        return RedistributionService(db).mark_transfer_delivered(
            transfer_id, current_user
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_service_error(exc)
