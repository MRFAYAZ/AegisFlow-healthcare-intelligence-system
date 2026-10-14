from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.dispatch import DispatchStatusEnum


class DispatchAssignmentRequest(BaseModel):
    transport_type: str = Field(min_length=2, max_length=100)
    vehicle_reference: str | None = Field(default=None, max_length=100)


class DispatchResponse(BaseModel):
    dispatch_id: UUID
    transfer_id: UUID
    dispatcher_id: UUID | None
    transport_type: str | None
    vehicle_reference: str | None
    status: DispatchStatusEnum
    dispatched_at: datetime | None
    estimated_arrival_at: datetime | None
    delivered_at: datetime | None
