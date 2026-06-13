import uuid

from sqlalchemy import (
    String,
    Text,
    TIMESTAMP
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.models.base import Base


class UserSession(Base):

    __tablename__ = "user_sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True)
    )

    jwt_token: Mapped[str] = mapped_column(
        Text
    )

    ip_address: Mapped[str] = mapped_column(
        String(100)
    )

    user_agent: Mapped[str] = mapped_column(
        Text
    )

    expires_at: Mapped[str] = mapped_column(
        TIMESTAMP
    )

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP
    )