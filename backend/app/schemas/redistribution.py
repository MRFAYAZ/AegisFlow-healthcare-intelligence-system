from uuid import UUID
from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
)

from app.core.enums import (
    TransferStatusEnum,
)

from app.schemas.common import (
    BaseSchema,
)


# =========================================================
# CREATE TRANSFER REQUEST
# =========================================================

class TransferRequestCreate(BaseModel):

    from_facility_id: UUID

    emergency_case_id: UUID | None = None

    to_facility_id: UUID

    medicine_id: UUID

    requested_quantity: int = Field(
        gt=0
    )


# =========================================================
# TRANSFER APPROVAL
# =========================================================

class TransferApprovalRequest(BaseModel):

    approved_quantity: int = Field(
        gt=0
    )

    reason : str | None = Field(
        default=None,
        min_length=5,
        max_length=1000
    )


# =========================================================
# TRANSFER REJECTION
# =========================================================

class TransferRejectionRequest(BaseModel):

    reason: str = Field(
        min_length=5,
        max_length=1000
    )


class TransferDispatchAssignmentRequest(BaseModel):

    transport_type: str = Field(
        min_length=2,
        max_length=100,
    )

    vehicle_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


# =========================================================
# TRANSFER RESPONSE
# =========================================================

class TransferResponse(BaseSchema):

    transfer_id: UUID

    emergency_case_id: UUID | None = None

    from_facility_id: UUID
    from_facility_name: str

    to_facility_id: UUID
    to_facility_name: str

    medicine_id: UUID
    medicine_name: str

    requested_quantity: int

    approved_quantity: int | None = None

    transfer_status: TransferStatusEnum

    cascade_safe: bool

    match_score: float | None = None

    transfer_distance_km: float | None = None

    recommendation_reason: str | None = None

    requested_by: UUID | None = None

    approved_by: UUID | None = None

    approved_at: datetime | None = None

    requested_at: datetime

    completed_at: datetime | None = None