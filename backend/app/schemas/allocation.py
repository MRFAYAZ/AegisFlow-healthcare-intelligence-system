from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.core.enums import AllocationLineStatusEnum, AllocationPlanStatusEnum
from app.schemas.common import BaseSchema


class AllocationLineApproval(BaseSchema):
    allocation_line_id: UUID
    approved_quantity: int = Field(gt=0)


class AllocationApprovalRequest(BaseSchema):
    lines: list[AllocationLineApproval] = Field(min_length=1)


class AllocationApprovalResponse(BaseSchema):
    message: str
    allocation_plan_id: UUID
    status: AllocationPlanStatusEnum
    allocated_quantity: int
    fulfillment_percentage: Decimal
    transfer_ids: list[UUID]


class AllocationLineResponse(BaseSchema):
    allocation_line_id: UUID
    allocation_plan_id: UUID
    source_facility_id: UUID
    medicine_id: UUID
    match_id: UUID | None = None
    recommended_quantity: int
    approved_quantity: int
    source_available_quantity: int
    source_safe_transferable_quantity: int
    distance_km: Decimal
    allocation_score: Decimal
    allocation_reason: str | None = None
    status: AllocationLineStatusEnum
    created_at: datetime
    updated_at: datetime


class AllocationPlanResponse(BaseSchema):
    allocation_plan_id: UUID
    emergency_case_id: UUID
    medicine_id: UUID
    requested_quantity: int
    recommended_quantity: int
    allocated_quantity: int
    fulfillment_percentage: Decimal
    optimization_score: Decimal | None = None
    status: AllocationPlanStatusEnum
    recommendation_reason: str | None = None
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    allocation_lines: list[AllocationLineResponse]