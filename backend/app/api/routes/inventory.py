from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_roles
from app.core.database import get_db
from app.core.enums import UserRoleEnum
from app.models.user import User
from app.services.inventory.forecast_service import ForecastService
from app.services.inventory.inventory_service import InventoryService
from app.schemas.inventory import (
    InventoryListResponse,
    InventoryResponse,
    StockoutForecastResponse,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])

INVENTORY_READ_ROLES = [
    UserRoleEnum.SYSTEM_ADMIN,
    UserRoleEnum.EMERGENCY_OPERATOR,
    UserRoleEnum.HOSPITAL_ADMIN,
    UserRoleEnum.PHARMACIST,
    UserRoleEnum.SHOP_OWNER,
    UserRoleEnum.SUPPLIER,
]


@router.get("", response_model=list[InventoryListResponse])
def get_all_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(INVENTORY_READ_ROLES)),
):
    try:
        return InventoryService(db).get_all_inventory(current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/forecast", response_model=list[StockoutForecastResponse])
def get_stockout_forecasts(
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
        return ForecastService(db).get_forecasts(current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/facility/{facility_id}", response_model=list[InventoryResponse])
def get_inventory_by_facility(
    facility_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(INVENTORY_READ_ROLES)),
):
    try:
        return InventoryService(db).get_inventory_by_facility_for_user(
            facility_id, current_user
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/critical", response_model=list[InventoryResponse])
def get_critical_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(INVENTORY_READ_ROLES)),
):
    try:
        return InventoryService(db).get_critical_inventory(current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/dashboard")
def get_inventory_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(INVENTORY_READ_ROLES)),
):
    try:
        return InventoryService(db).get_dashboard(current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
