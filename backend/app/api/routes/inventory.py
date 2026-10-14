from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.inventory.inventory_service import (
    InventoryService
)

from app.schemas.inventory import (
    InventoryResponse
)

from app.schemas.inventory import (
    InventoryListResponse,
    StockoutForecastResponse,
)

from app.api.dependencies.auth import require_roles
from app.core.enums import UserRoleEnum
from app.models.user import User
from app.services.inventory.forecast_service import ForecastService

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


# =====================================================
# GET ALL INVENTORY
# =====================================================

@router.get(
    "",
    response_model=list[InventoryListResponse]
)
def get_all_inventory(
    db: Session = Depends(get_db)
):

    service = InventoryService(db)

    return service.get_all_inventory()


# =====================================================
# GET INVENTORY BY FACILITY
# =====================================================

@router.get(
    "/facility/{facility_id}",
    response_model=list[InventoryResponse]
)
def get_inventory_by_facility(
    facility_id: UUID,
    db: Session = Depends(get_db)
):

    service = InventoryService(db)

    return service.get_inventory_by_facility(
        facility_id
    )


# =====================================================
# GET CRITICAL INVENTORY
# =====================================================

@router.get(
    "/critical",
    response_model=list[InventoryResponse]
)
def get_critical_inventory(
    db: Session = Depends(get_db)
):

    service = InventoryService(db)

    return service.get_critical_inventory()


# =====================================================
# STOCKOUT FORECAST INTELLIGENCE
# =====================================================

@router.get(
    "/forecast",
    response_model=list[StockoutForecastResponse],
    summary="Project stockout risk from current stock and replenishment lead time",
)
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


# =====================================================
# INVENTORY DASHBOARD
# =====================================================

@router.get(
    "/dashboard"
)
def get_inventory_dashboard(
    db: Session = Depends(get_db)
):

    service = InventoryService(db)

    return service.get_dashboard()