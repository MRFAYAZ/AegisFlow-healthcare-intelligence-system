import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.core.enums import DispatchStatusEnum


class TransferDispatch(Base, TimestampMixin):
    """Operational dispatch record for one approved transfer."""

    __tablename__ = "transfer_dispatches"

    dispatch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    transfer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transfer_requests.transfer_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    dispatcher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    transport_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    vehicle_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    status: Mapped[DispatchStatusEnum] = mapped_column(
        Enum(DispatchStatusEnum, name="dispatchstatusenum"),
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

    transfer = relationship("TransferRequest", back_populates="dispatch")
