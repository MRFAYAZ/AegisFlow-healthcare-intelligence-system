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

from uuid import UUID

from pydantic import BaseModel, Field


class StockoutForecastResponse(BaseModel):
    inventory_id: UUID
    facility_id: UUID
    facility_name: str
    medicine_id: UUID
    medicine_name: str
    available_stock: int = Field(ge=0)
    reserved_stock: int = Field(ge=0)
    batch_verified_usable_stock: int = Field(ge=0)
    expired_batch_quantity: int = Field(ge=0)
    batch_traceability: str
    eligible_batch_count: int = Field(ge=0)
    usable_stock: int = Field(ge=0)
    daily_consumption_rate: float = Field(ge=0)
    lead_time_days: int = Field(ge=0)
    safety_stock_days: int = Field(ge=0)
    projected_stockout_days: float | None = Field(default=None, ge=0)
    risk_score: float | None = Field(default=None, ge=0, le=100)
    risk_level: str
    recommended_action: str
    explanation: str
