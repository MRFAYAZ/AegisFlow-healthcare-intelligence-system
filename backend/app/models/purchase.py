import uuid

from sqlalchemy import (
    String,
    Integer,
    DECIMAL,
    ForeignKey,
    Enum,
    Boolean,
    TIMESTAMP
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, TimestampMixin

from app.core.enums import PurchaseStatusEnum


# =========================================================
# PURCHASE TRANSACTION
# =========================================================

class PurchaseTransaction(Base, TimestampMixin):
    __tablename__ = "purchase_transactions"

    purchase_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    facility_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("facilities.facility_id"),
        nullable=False
    )

    medicine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("medicine_master.medicine_id"),
        nullable=False
    )

    customer_name: Mapped[str] = mapped_column(
        String(255)
    )

    customer_phone: Mapped[str] = mapped_column(
        String(20)
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    unit_price: Mapped[float] = mapped_column(
        DECIMAL(10, 2),
        nullable=False
    )

    total_amount: Mapped[float] = mapped_column(
        DECIMAL(10, 2),
        nullable=False
    )

    purchase_status: Mapped[PurchaseStatusEnum] = mapped_column(
        Enum(PurchaseStatusEnum),
        default=PurchaseStatusEnum.PENDING
    )

    stock_reduced: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    purchased_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True)
    )

    facility = relationship("Facility")

    medicine = relationship("Medicine")