import uuid

from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    Enum
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, TimestampMixin
from app.core.enums import FacilityTypeEnum

class Facility(Base, TimestampMixin):
    __tablename__ = "facilities"

    facility_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    facility_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    facility_type: Mapped[FacilityTypeEnum] = mapped_column(
        Enum(FacilityTypeEnum),
        nullable=False
    )

    location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("locations.location_id"),
        nullable=False
    )

    license_number: Mapped[str] = mapped_column(
        String(100)
    )

    contact_email: Mapped[str] = mapped_column(
        String(255)
    )

    contact_phone: Mapped[str] = mapped_column(
        String(20)
    )

    emergency_contact: Mapped[str] = mapped_column(
        String(20)
    )

    is_24x7: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    location = relationship(
        "Location",
        back_populates="facilities"
    )

    inventories = relationship(
        "InventoryCurrent",
        back_populates="facility"
    )

    