import uuid

from sqlalchemy import (
    String,
    Boolean,
    Integer,
    DECIMAL,
    Text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, TimestampMixin


class Medicine(Base, TimestampMixin):
    __tablename__ = "medicine_master"

    medicine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    medicine_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    medicine_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    generic_name: Mapped[str] = mapped_column(
        String(255)
    )

    category: Mapped[str] = mapped_column(
        String(100)
    )

    dosage_form: Mapped[str] = mapped_column(
        String(50)
    )

    strength: Mapped[str] = mapped_column(
        String(50)
    )

    manufacturer: Mapped[str] = mapped_column(
        String(255)
    )

    prescription_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_critical: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    storage_conditions: Mapped[str] = mapped_column(
        Text
    )

    standard_lead_time_days: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    safety_stock_days: Mapped[int] = mapped_column(
        Integer,
        default=3
    )

    unit_price: Mapped[float] = mapped_column(
        DECIMAL(10, 2)
    )

    expiry_alert_days: Mapped[int] = mapped_column(
        Integer,
        default=30
    )

    inventories = relationship(
        "InventoryCurrent",
        back_populates="medicine"
    )