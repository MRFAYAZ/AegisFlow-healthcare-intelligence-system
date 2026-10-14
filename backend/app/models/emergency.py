import uuid

from sqlalchemy import (
    Integer,
    DECIMAL,
    ForeignKey,
    Enum,
    TIMESTAMP,
    Boolean,
    String,
    Date,
    Text,
    JSON,
)


from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import (
    Base,
    TimestampMixin
)

from app.core.enums import (
    SeverityEnum,
    EmergencyStatusEnum
)


# =========================================================
# EMERGENCY CASE
# =========================================================

class EmergencyCase(Base, TimestampMixin):

    __tablename__ = "emergency_cases"

    emergency_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    transfer_requests = relationship(
        "TransferRequest",
        back_populates="emergency_case"
    )

    facility_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("facilities.facility_id"),
        nullable=False
    )

    medicine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("medicine_master.medicine_id"),
        nullable=False
    )

    shortage_score: Mapped[float] = mapped_column(
        DECIMAL(5, 2),
        nullable=False
    )

    severity: Mapped[SeverityEnum] = mapped_column(
        Enum(SeverityEnum),
        nullable=False
    )

    emergency_radius_km: Mapped[int] = mapped_column(
        Integer,
        default=5
    )

    required_quantity: Mapped[int] = mapped_column(
        Integer
    )

    available_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    emergency_status: Mapped[EmergencyStatusEnum] = mapped_column(
        Enum(EmergencyStatusEnum),
        default=EmergencyStatusEnum.ACTIVE
    )

    triggered_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True)
    )

    resolved_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True)
    )

    allocation_plan = relationship(
        "EmergencyAllocationPlan",
        back_populates="emergency_case",
        uselist=False
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    facility = relationship(
        "Facility"
    )

    medicine = relationship(
        "Medicine"
    )


# =========================================================
# EMERGENCY SOURCE MATCH
# =========================================================

class EmergencySourceMatch(Base, TimestampMixin):

    __tablename__ = "emergency_source_matches"

    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    emergency_case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("emergency_cases.emergency_case_id"),
        nullable=False
    )

    source_facility_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("facilities.facility_id"),
        nullable=False
    )

    medicine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("medicine_master.medicine_id"),
        nullable=False
    )

    # =====================================================
    # INVENTORY
    # =====================================================

    available_quantity: Mapped[int] = mapped_column(
        Integer
    )

    transferable_quantity: Mapped[int] = mapped_column(
        Integer
    )

    selected_batch_number: Mapped[str | None] = mapped_column(String(100))
    earliest_expiry_date: Mapped[str | None] = mapped_column(Date)
    cold_chain_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cold_chain_capable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    safety_status: Mapped[str] = mapped_column(String(40), default="LEGACY_UNVALIDATED", nullable=False)
    safety_reason: Mapped[str | None] = mapped_column(Text)
    batch_allocations: Mapped[list | None] = mapped_column(JSON)

    # =====================================================
    # DISTANCE
    # =====================================================

    distance_km: Mapped[float] = mapped_column(
        DECIMAL(10, 2)
    )

    distance_score: Mapped[float] = mapped_column(
        DECIMAL(5, 4)
    )

    # =====================================================
    # DONOR HEALTH
    # =====================================================

    donor_shortage_score: Mapped[float] = mapped_column(
        DECIMAL(5, 2)
    )

    donor_health_score: Mapped[float] = mapped_column(
        DECIMAL(5, 4)
    )

    # =====================================================
    # INVENTORY MATCH SCORE
    # =====================================================

    inventory_score: Mapped[float] = mapped_column(
        DECIMAL(5, 4)
    )

    # =====================================================
    # FINAL RANKING
    # =====================================================

    ranking_score: Mapped[float] = mapped_column(
        DECIMAL(5, 2)
    )

    # =====================================================
    # SELECTION
    # =====================================================

    is_selected: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    matched_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True)
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    emergency_case = relationship(
        "EmergencyCase"
    )

    source_facility = relationship(
        "Facility"
    )

    medicine = relationship(
        "Medicine"
    )