from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class AvailabilitySnapshotRequest(BaseModel):
    medicine_id: UUID
    total_stock: int = Field(ge=0)
    available_stock: int = Field(ge=0)
    reserved_stock: int = Field(ge=0)
    minimum_threshold: int = Field(ge=0)
    observed_at: datetime
    source_system: str = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_stock_levels(self):
        if self.available_stock + self.reserved_stock > self.total_stock:
            raise ValueError("Available and reserved stock cannot exceed total stock.")
        if self.minimum_threshold > self.total_stock:
            raise ValueError("Minimum threshold cannot exceed total stock.")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must include a timezone.")
        return self


class VisibilityUpdateRequest(BaseModel):
    enabled: bool


class NetworkSearchRequest(BaseModel):
    requester_facility_id: UUID
    medicine_id: UUID
    required_quantity: int = Field(gt=0)
    radius_km: float = Field(default=50, gt=0, le=500)
    emergency_override: bool = False


class NetworkOfferResponse(BaseModel):
    facility_id: UUID
    facility_name: str
    facility_type: str
    safe_transferable_quantity: int
    distance_km: float
    score: float
    batch_traceability_available: bool
    cold_chain_eligible: bool
    recommendation_reason: str