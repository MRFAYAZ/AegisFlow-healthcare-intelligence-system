from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums import SeverityEnum, SupplyRequestStatusEnum
from app.schemas.common import BaseSchema


class ReplenishmentRequirementResponse(BaseSchema):
    requirement_id: UUID | None
    inventory_id: UUID
    facility_id: UUID
    medicine_id: UUID
    facility_name: str
    medicine_name: str
    requested_quantity: int
    priority: str
    projected_stockout_days: float | None
    required_by_days: int | None
    reason: str
    status: str


class SupplierRecommendationResponse(BaseSchema):
    supplier_facility_id: UUID
    supplier_name: str
    medicine_id: UUID
    medicine_name: str
    available_quantity: int
    requested_quantity: int
    lead_time_days: int
    distance_km: float | None
    readiness_score: float
    reliability_status: str
    recommendation_reason: str


class SupplyRequestCreate(BaseModel):
    inventory_id: UUID
    supplier_facility_id: UUID
    requested_quantity: int = Field(gt=0)


class SupplyRequestDecision(BaseModel):
    accepted_quantity: int = Field(ge=0)
    response_note: str | None = None


class SupplyRequestResponse(BaseSchema):
    request_id: UUID
    requirement_id: UUID
    supplier_facility_id: UUID
    supplier_name: str
    target_facility_id: UUID
    target_facility_name: str
    medicine_id: UUID
    medicine_name: str
    requested_quantity: int
    accepted_quantity: int
    lead_time_days: int
    recommendation_score: float
    status: SupplyRequestStatusEnum
    created_at: datetime