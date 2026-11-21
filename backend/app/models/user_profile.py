import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", "profile_code", name="uq_user_profile_code"),
    )

    profile_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False,
    )

    profile_code = Column(
        String(80),
        nullable=False,
    )

    profile_name = Column(
        String(120),
        nullable=False,
    )

    module_access = Column(
        String,
        nullable=False,
        default="[]",
    )

    is_default = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
    )
