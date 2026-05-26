import uuid

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

    requested_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    approved_quantity: Mapped[int] = mapped_column(
        Integer
    )

    transfer_status: Mapped[TransferStatusEnum] = mapped_column(
        Enum(TransferStatusEnum),
        default=TransferStatusEnum.PENDING
    )

    cascade_safe: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    match_score: Mapped[float] = mapped_column(
        DECIMAL(5, 2)
    )

    transfer_distance_km: Mapped[float] = mapped_column(
        DECIMAL(10, 2)
    )

    recommendation_reason: Mapped[str] = mapped_column(
        Text
    )

    requested_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True)
    )

    completed_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True)
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