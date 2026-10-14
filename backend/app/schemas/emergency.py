from uuid import UUID
from datetime import datetime

from pydantic import (
    BaseModel,
    Field
)

from app.core.enums import (
    SeverityEnum,
    EmergencyStatusEnum,
    TransferStatusEnum,
    DispatchStatusEnum
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
    facility_name: str
    facility_latitude: float | None = None
    facility_longitude: float | None = None

    medicine_id: UUID
    medicine_name: str

    shortage_score: float

    severity: SeverityEnum

    emergency_radius_km: int

    required_quantity: int

    available_quantity: int

    emergency_status: EmergencyStatusEnum

    triggered_at: datetime

    resolved_at: datetime | None = None

    # ---------------------------
    # AI Recommendation
    # ---------------------------

    transfer_id: UUID | None = None

    donor_facility: str | None = None
    donor_latitude: float | None = None
    donor_longitude: float | None = None

    transfer_status: TransferStatusEnum | None = None

    approved_quantity: int | None = None

    match_score: float | None = None

    transfer_distance_km: float | None = None

    cascade_safe: bool | None = None

    estimated_eta_minutes: int | None = None

    ai_reason: str | None = None

    alternative_donors: int | None = None

    requested_at: datetime | None = None
    approved_at: datetime | None = None
    completed_at: datetime | None = None
    rejection_reason: str | None = None
    dispatch_status: DispatchStatusEnum | None = None
    transport_type: str | None = None
    vehicle_reference: str | None = None
    dispatched_at: datetime | None = None
    delivered_at: datetime | None = None
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