import uuid

from sqlalchemy import (
    String,
    JSON,
    TIMESTAMP,
    Enum
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.models.base import Base

from app.core.enums import (
    EventTypeEnum
)


class EventLog(Base):

    __tablename__ = "event_log"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True
    )

    event_type: Mapped[EventTypeEnum] = mapped_column(
        Enum(EventTypeEnum)
    )

    entity_type: Mapped[str] = mapped_column(
        String(100)
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True)
    )

    event_payload: Mapped[dict] = mapped_column(
        JSON
    )

    triggered_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True)
    )

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP
    )