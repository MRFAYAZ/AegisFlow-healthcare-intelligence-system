import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, JSON, String, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class IntegrationEvent(Base):
    """Idempotency receipt for an externally supplied inventory snapshot."""

    __tablename__ = "integration_events"
    __table_args__ = (
        UniqueConstraint("source_id", "external_event_id", name="uq_integration_source_event"),
    )

    integration_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("integration_sources.source_id", ondelete="CASCADE"),
        nullable=False,
    )
    external_event_id: Mapped[str] = mapped_column(String(255), nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    source_timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    records_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    response_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    received_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
