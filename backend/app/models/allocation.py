import uuid

from datetime import datetime

from sqlalchemy import (
    Integer,
    DECIMAL,
    ForeignKey,
    Enum,
    Text,
    TIMESTAMP,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import (
    Base,
    TimestampMixin,
)

from app.core.enums import (
    AllocationPlanStatusEnum,
    AllocationLineStatusEnum,
)


# =========================================================
# EMERGENCY ALLOCATION PLAN
# =========================================================

class EmergencyAllocationPlan(
    Base,
    TimestampMixin
):

    __tablename__ = "emergency_allocation_plans"

    allocation_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    emergency_case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "emergency_cases.emergency_case_id"
        ),
        nullable=False,
        unique=True,
    )

    medicine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "medicine_master.medicine_id"
        ),
        nullable=False,
    )

    requested_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    recommended_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    allocated_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    fulfillment_percentage: Mapped[float] = mapped_column(
        DECIMAL(5, 2),
        default=0,
        nullable=False,
    )

    optimization_score: Mapped[float | None] = mapped_column(
        DECIMAL(8, 4),
        nullable=True,
    )

    status: Mapped[AllocationPlanStatusEnum] = mapped_column(
        Enum(AllocationPlanStatusEnum),
        default=AllocationPlanStatusEnum.DRAFT,
        nullable=False,
    )

    recommendation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    emergency_case = relationship(
        "EmergencyCase",
    )

    medicine = relationship(
        "Medicine",
    )

    allocation_lines = relationship(
        "EmergencyAllocationLine",
        back_populates="allocation_plan",
        cascade="all, delete-orphan",
    )


# =========================================================
# EMERGENCY ALLOCATION LINE
# =========================================================

class EmergencyAllocationLine(
    Base,
    TimestampMixin
):

    __tablename__ = "emergency_allocation_lines"

    allocation_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    allocation_plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "emergency_allocation_plans.allocation_plan_id"
        ),
        nullable=False,
    )

    source_facility_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "facilities.facility_id"
        ),
        nullable=False,
    )

    medicine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "medicine_master.medicine_id"
        ),
        nullable=False,
    )

    match_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "emergency_source_matches.match_id"
        ),
        nullable=True,
    )

    recommended_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    approved_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    source_available_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    source_safe_transferable_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    distance_km: Mapped[float] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
    )

    allocation_score: Mapped[float] = mapped_column(
        DECIMAL(8, 4),
        nullable=False,
    )

    allocation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[AllocationLineStatusEnum] = mapped_column(
        Enum(AllocationLineStatusEnum),
        default=AllocationLineStatusEnum.RECOMMENDED,
        nullable=False,
    )

    allocation_plan = relationship(
        "EmergencyAllocationPlan",
        back_populates="allocation_lines",
    )

    source_facility = relationship(
        "Facility",
    )

    medicine = relationship(
        "Medicine",
    )

    source_match = relationship(
        "EmergencySourceMatch",
    )