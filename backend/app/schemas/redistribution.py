from uuid import UUID
from datetime import datetime

from pydantic import (
    BaseModel,
    Field
)

from app.core.enums import (
    TransferStatusEnum
)

from app.schemas.common import (
    BaseSchema
)


# =========================================================
# CREATE TRANSFER REQUEST
# =========================================================

class TransferRequestCreate(BaseModel):

    from_facility_id: UUID

    to_facility_id: UUID

    medicine_id: UUID

    requested_quantity: int = Field(
        gt=0
    )


# =========================================================
# TRANSFER RESPONSE
# =========================================================

class TransferResponse(BaseSchema):

    transfer_id: UUID

    from_facility_id: UUID

    to_facility_id: UUID

    medicine_id: UUID

    requested_quantity: int

    approved_quantity: int | None = None

    transfer_status: TransferStatusEnum

    cascade_safe: bool

    match_score: float | None = None

    transfer_distance_km: float | None = None

    recommendation_reason: str | None = None

    requested_at: datetime

    completed_at: datetime | None = None