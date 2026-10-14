import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, JSON, String, Text, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EmergencyTimelineEvent(Base):
    """Append-only operational event for tracing emergency response decisions."""

    __tablename__ = "emergency_timeline_events"

    timeline_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    emergency_case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("emergency_cases.emergency_case_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transfer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("transfer_requests.transfer_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    event_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
