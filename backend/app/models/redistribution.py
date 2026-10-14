import uuid
from datetime import datetime

from sqlalchemy import (
    Integer,
    DECIMAL,
    Boolean,
    ForeignKey,
    Enum,
    Text,
    TIMESTAMP
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, TimestampMixin

from app.core.enums import TransferStatusEnum


# =========================================================
# TRANSFER REQUEST
# =========================================================

class TransferRequest(Base, TimestampMixin):
    __tablename__ = "transfer_requests"

    transfer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    from_facility_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("facilities.facility_id"),
        nullable=False
    )

    to_facility_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("facilities.facility_id"),
        nullable=False
    )

    medicine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("medicine_master.medicine_id"),
        nullable=False
    )

    emergency_case_id: Mapped[uuid.UUID | None]  = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("emergency_cases.emergency_case_id"),
        nullable=True
    )

    emergency_case = relationship(
        "EmergencyCase",
        back_populates="transfer_requests"
    )

    requested_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    approved_quantity: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    requested_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )

    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    rejection_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    transfer_status: Mapped[TransferStatusEnum] = mapped_column(
        Enum(TransferStatusEnum),
        default=TransferStatusEnum.PENDING
    )

    cascade_safe: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    match_score: Mapped[float | None] = mapped_column(
        DECIMAL(5, 2),
        nullable=True
    )

    transfer_distance_km: Mapped[float | None] = mapped_column(
        DECIMAL(10, 2),
        nullable=True
    )

    recommendation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    requested_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    source_facility = relationship(
        "Facility",
        foreign_keys=[from_facility_id]
    )

    destination_facility = relationship(
        "Facility",
        foreign_keys=[to_facility_id]
    )

    medicine = relationship("Medicine")

    dispatch = relationship(
        "TransferDispatch",
        back_populates="transfer",
        uselist=False
    )
    
    batch_allocations = relationship(
        "TransferBatchAllocation",
        back_populates="transfer",
        cascade="all, delete-orphan"
    )
