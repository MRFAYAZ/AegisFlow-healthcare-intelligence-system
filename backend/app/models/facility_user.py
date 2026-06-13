import uuid

from sqlalchemy import (
    ForeignKey,
    Enum,
    TIMESTAMP
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base

from app.core.enums import UserRoleEnum


class FacilityUser(Base):

    __tablename__ = "facility_users"

    facility_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    facility_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("facilities.facility_id")
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id")
    )

    assigned_role: Mapped[UserRoleEnum] = mapped_column(
        Enum(UserRoleEnum)
    )

    assigned_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True)
    )