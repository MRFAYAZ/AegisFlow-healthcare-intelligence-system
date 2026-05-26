from sqlalchemy import String, Text, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography

from app.models.base import Base, TimestampMixin
import uuid

class Location(Base, TimestampMixin):
    __tablename__ = "locations"

    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    country: Mapped[str] = mapped_column(
        String(100),
        default="India"
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    district: Mapped[str] = mapped_column(
        String(100)
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    postal_code: Mapped[str] = mapped_column(
        String(20)
    )

    address_line: Mapped[str] = mapped_column(
        Text
    )

    latitude: Mapped[float] = mapped_column(
        DECIMAL(10, 7),
        nullable=False
    )

    longitude: Mapped[float] = mapped_column(
        DECIMAL(10, 7),
        nullable=False
    )

    geo_point = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )

    facilities = relationship(
        "Facility",
        back_populates="location"
    )