import uuid

from sqlalchemy import (
    String,
    JSON
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.models.base import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True)
    )

    action_type: Mapped[str] = mapped_column(
        String(100)
    )

    entity_type: Mapped[str] = mapped_column(
        String(100)
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True)
    )

    old_value: Mapped[dict] = mapped_column(
        JSON
    )

    new_value: Mapped[dict] = mapped_column(
        JSON
    )

    ip_address: Mapped[str] = mapped_column(
        String(100)
    )