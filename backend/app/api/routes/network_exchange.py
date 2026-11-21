from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user, require_roles
from app.core.database import get_db
from app.core.enums import UserRoleEnum
from app.models.user import User
from app.schemas.network_exchange import (
    AvailabilitySnapshotRequest,
    NetworkOfferResponse,
    NetworkSearchRequest,
    VisibilityUpdateRequest,
)
from app.schemas.facility import FacilityResponse
from app.services.network_exchange_service import NetworkExchangeService

router = APIRouter(tags=["Network Exchange", "Integrations"])

PARTICIPANT_ROLES = [
    UserRoleEnum.HOSPITAL_ADMIN,
    UserRoleEnum.PHARMACIST,
    UserRoleEnum.SHOP_OWNER,
    UserRoleEnum.SUPPLIER,
    UserRoleEnum.SYSTEM_ADMIN,
    UserRoleEnum.EMERGENCY_OPERATOR,
]


@router.get(
    "/network-exchange/facilities",
    response_model=list[FacilityResponse],
)
def get_accessible_facilities(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(PARTICIPANT_ROLES)),
):
    return NetworkExchangeService(db).get_accessible_facilities(current_user)


@router.put(
    "/integrations/facilities/{facility_id}/availability",
    status_code=status.HTTP_200_OK,
)
def sync_availability(
    facility_id: UUID,
    payload: AvailabilitySnapshotRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(PARTICIPANT_ROLES)),
):
    try:
        inventory = NetworkExchangeService(db).update_availability(
            facility_id,
            payload,
            current_user,
        )
        db.commit()
        return {
            "status": "accepted",
            "facility_id": facility_id,
            "medicine_id": inventory.medicine_id,
            "observed_at": inventory.external_observed_at,
        }
    except PermissionError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        db.rollback()
        code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=code, detail=str(exc))


@router.patch("/network-exchange/facilities/{facility_id}/visibility")
def update_visibility(
    facility_id: UUID,
    payload: VisibilityUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(PARTICIPANT_ROLES)),
):
    try:
        facility = NetworkExchangeService(db).set_visibility(
            facility_id,
            payload.enabled,
            current_user,
        )
        db.commit()
        return {
            "facility_id": facility.facility_id,
            "network_visibility_enabled": facility.network_visibility_enabled,
        }
    except PermissionError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/network-exchange/search",
    response_model=list[NetworkOfferResponse],
)
def search_network_offers(
    payload: NetworkSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = UserRoleEnum(current_user.role)
    if payload.emergency_override and role not in {
        UserRoleEnum.EMERGENCY_OPERATOR,
        UserRoleEnum.SYSTEM_ADMIN,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Emergency visibility override requires emergency-operator access.",
        )
    try:
        return NetworkExchangeService(db).search_offers(
            requester_facility_id=payload.requester_facility_id,
            medicine_id=payload.medicine_id,
            required_quantity=payload.required_quantity,
            radius_km=payload.radius_km,
            emergency_override=payload.emergency_override,
            actor=current_user,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))