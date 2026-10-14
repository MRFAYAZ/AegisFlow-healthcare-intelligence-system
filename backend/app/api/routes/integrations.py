from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.core.database import get_db
from app.core.enums import UserRoleEnum
from app.models.user import User
from app.schemas.integration import (
    IntegrationEventResponse,
    IntegrationInventorySnapshotRequest,
    IntegrationMedicineMappingCreate,
    IntegrationMedicineMappingResponse,
    IntegrationSnapshotResponse,
    IntegrationSourceCreate,
    IntegrationSourceCreated,
    IntegrationSourceResponse,
)
from app.services.integration_service import (
    IntegrationService,
    InvalidIntegrationCredential,
)

router = APIRouter(prefix="/integrations", tags=["External System Integrations"])


@router.post("/sources", response_model=IntegrationSourceCreated, status_code=201)
def create_integration_source(
    payload: IntegrationSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.SYSTEM_ADMIN])),
):
    try:
        return IntegrationService(db).create_source(payload, current_user)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/sources", response_model=list[IntegrationSourceResponse])
def list_integration_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.SYSTEM_ADMIN])),
):
    return IntegrationService(db).list_sources()


@router.get(
    "/sources/{source_id}/events",
    response_model=list[IntegrationEventResponse],
    summary="List the last 100 successfully accepted snapshot receipts",
)
def list_snapshot_events(
    source_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.SYSTEM_ADMIN])),
):
    try:
        return IntegrationService(db).list_snapshot_events(source_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/sources/{source_id}/disable", response_model=IntegrationSourceResponse)
def disable_integration_source(
    source_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.SYSTEM_ADMIN])),
):
    try:
        return IntegrationService(db).deactivate_source(source_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/sources/{source_id}/rotate-key", response_model=IntegrationSourceCreated)
def rotate_integration_key(
    source_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.SYSTEM_ADMIN])),
):
    try:
        return IntegrationService(db).rotate_source_key(source_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/sources/{source_id}/medicine-mappings",
    response_model=IntegrationMedicineMappingResponse,
)
def create_or_update_medicine_mapping(
    source_id: UUID,
    payload: IntegrationMedicineMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.SYSTEM_ADMIN])),
):
    try:
        return IntegrationService(db).create_or_update_medicine_mapping(source_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/sources/{source_id}/medicine-mappings",
    response_model=list[IntegrationMedicineMappingResponse],
)
def list_medicine_mappings(
    source_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.SYSTEM_ADMIN])),
):
    try:
        return IntegrationService(db).list_medicine_mappings(source_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/inventory/snapshot",
    response_model=IntegrationSnapshotResponse,
    summary="Ingest a replay-safe batch-level inventory snapshot from an external system",
    description=(
        "Authenticate with X-Integration-Key. A key is restricted to one facility and "
        "its configured medicine mappings. Each snapshot must contain a unique external "
        "event ID, a timezone-aware source timestamp, and a complete batch-level stock "
        "view for each medicine. Inventory, batch reservations and the idempotency receipt "
        "are committed atomically."
    ),
)
def ingest_inventory_snapshot(
    payload: IntegrationInventorySnapshotRequest,
    integration_key: str | None = Header(default=None, alias="X-Integration-Key"),
    db: Session = Depends(get_db),
):
    try:
        return IntegrationService(db).ingest_inventory_snapshot(integration_key, payload)
    except InvalidIntegrationCredential as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Integration-Key"},
        ) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
