from uuid import UUID

from pydantic import (
    BaseModel,
    Field
)

from app.core.enums import (
    SeverityEnum
)

from app.schemas.common import (
    BaseSchema
)


# =========================================================
# CREATE INVENTORY
# =========================================================

class InventoryCreate(BaseModel):

    facility_id: UUID

    medicine_id: UUID

    total_stock: int = Field(
        ge=0
    )

    available_stock: int = Field(
        ge=0
    )

    reserved_stock: int = Field(
        ge=0
    )

    minimum_threshold: int = Field(
        ge=0
    )

    reorder_threshold: int = Field(
        ge=0
    )

    daily_consumption_rate: float = Field(
        ge=0
    )

    lead_time_days: int = Field(
        ge=0
    )


# =========================================================
# INVENTORY RESPONSE
# =========================================================

class InventoryResponse(BaseSchema):

    inventory_id: UUID

    facility_id: UUID

    medicine_id: UUID

    total_stock: int

    available_stock: int

    reserved_stock: int

    shortage_score: float

    severity: SeverityEnum

# =========================================================
# INVENTORY LIST RESPONSE
# =========================================================

class InventoryListResponse(BaseSchema):

    inventory_id: UUID

    facility_name: str

    medicine_name: str

    total_stock: int

    available_stock: int

    reserved_stock: int

    shortage_score: float

    severity: SeverityEnum