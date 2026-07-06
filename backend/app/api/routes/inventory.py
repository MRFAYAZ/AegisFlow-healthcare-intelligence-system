from uuid import UUID

from fastapi import (
    APIRouter,
    Depends
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
    InventoryListResponse
)

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