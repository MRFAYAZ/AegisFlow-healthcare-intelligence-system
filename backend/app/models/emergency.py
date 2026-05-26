import uuid

from sqlalchemy import (
    Integer,
    DECIMAL,
    ForeignKey,
    Enum,
    TIMESTAMP,
    Boolean
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, TimestampMixin

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

    facility = relationship("Facility")

    medicine = relationship("Medicine")


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

    available_quantity: Mapped[int] = mapped_column(
        Integer
    )

    transferable_quantity: Mapped[int] = mapped_column(
        Integer
    )

    distance_km: Mapped[float] = mapped_column(
        DECIMAL(10, 2)
    )

    ranking_score: Mapped[float] = mapped_column(
        DECIMAL(5, 2)
    )

    is_selected: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    matched_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True)
    )

    emergency_case = relationship("EmergencyCase")

    source_facility = relationship("Facility")

    medicine = relationship("Medicine")