"""Typed response for the explainable emergency donor matching API."""
from uuid import UUID

from pydantic import BaseModel, Field


class MatchScoreBreakdown(BaseModel):
    distance_score: float
    inventory_score: float
    donor_health_score: float
    distance_weight: float
    inventory_weight: float
    donor_health_weight: float


class EmergencyMatchResponse(BaseModel):
    rank: int = Field(ge=1)
    facility_id: UUID
    facility_name: str
    facility_type: str
    aggregate_available_quantity: int = Field(ge=0)
    available_quantity: int = Field(ge=0, description="Available stock supported by unexpired, batch-traceable lot records.")
    transferable_quantity: int = Field(ge=0)
    suggested_quantity: int = Field(ge=0)
    distance_km: float = Field(ge=0, description="Straight-line geographic distance, not road distance.")
    ranking_score: float = Field(ge=0, le=100)
    score_breakdown: MatchScoreBreakdown
    requires_cold_chain: bool
    cold_chain_capable: bool
    batch_traceability: str
    eligible_batch_count: int = Field(ge=0)
    nearest_expiry_date: str
    recommendation_reason: str
