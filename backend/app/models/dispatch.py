import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class DispatchStatusEnum(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    DISPATCHED = "DISPATCHED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TransferDispatch(Base, TimestampMixin):
    __tablename__ = "transfer_dispatches"

    dispatch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    transfer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transfer_requests.transfer_id"),
        nullable=False,
        unique=True,
    )

    dispatcher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    transport_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    vehicle_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[DispatchStatusEnum] = mapped_column(
        SAEnum(DispatchStatusEnum, name="dispatchstatusenum"),
        default=DispatchStatusEnum.PENDING,
        nullable=False,
    )

    dispatched_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    estimated_arrival_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    transfer = relationship(
        "TransferRequest",
        back_populates="dispatch",
    )
