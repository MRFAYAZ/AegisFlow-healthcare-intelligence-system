from uuid import UUID
from datetime import datetime

from pydantic import (
    BaseModel,
    Field
)

from app.core.enums import (
    SeverityEnum,
    EmergencyStatusEnum
)

from app.schemas.common import (
    BaseSchema
)


# =========================================================
# CREATE EMERGENCY CASE
# =========================================================

class EmergencyCreate(BaseModel):

    facility_id: UUID

    medicine_id: UUID

    shortage_score: float = Field(
        ge=0
    )

    severity: SeverityEnum

    emergency_radius_km: int = Field(
        ge=1,
        le=100
    )

    required_quantity: int = Field(
        gt=0
    )


# =========================================================
# EMERGENCY RESPONSE
# =========================================================

class EmergencyResponse(BaseSchema):

    emergency_case_id: UUID

    facility_id: UUID

    medicine_id: UUID

    shortage_score: float

    severity: SeverityEnum

    emergency_radius_km: int

    required_quantity: int

    available_quantity: int

    emergency_status: EmergencyStatusEnum

    triggered_at: datetime

    resolved_at: datetime | None = None


# =========================================================
# EMERGENCY MATCH RESPONSE
# =========================================================

class EmergencyMatchResponse(BaseSchema):

    match_id: UUID

    emergency_case_id: UUID

    source_facility_id: UUID

    medicine_id: UUID

    available_quantity: int

    transferable_quantity: int

    distance_km: float

    ranking_score: float

    is_selected: bool