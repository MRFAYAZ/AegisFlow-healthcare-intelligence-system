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


class ShortageRiskAssessment(BaseSchema):
    inventory_id: UUID
    facility_id: UUID
    medicine_id: UUID
    facility_name: str
    medicine_name: str
    current_stock: int
    reserved_stock: int
    usable_stock: int
    daily_consumption: float
    safety_stock_days: int
    safety_stock_units: float
    lead_time_days: int
    projected_stockout_days: float | None
    risk_score: float
    risk_level: str
    recommended_action: str