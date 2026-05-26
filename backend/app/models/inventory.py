import uuid

from sqlalchemy import (
    String,
    Integer,
    DECIMAL,
    ForeignKey,
    Date,
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
from app.core.enums import SeverityEnum

# =========================================================
# INVENTORY CURRENT
# =========================================================

class InventoryCurrent(Base, TimestampMixin):
    __tablename__ = "inventory_current"

    inventory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key = True,
        default = uuid.uuid4
    )
    
    facility_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("facilities.facility_id"),
        nullable = False
    )

    medicine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("medicine_master.medicine_id"),
        nullable = False
    )

    total_stock: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    available_stock: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    reserved_stock: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    minimum_threshold: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    reorder_threshold: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    daily_consumption_rate: Mapped[float] = mapped_column(
        DECIMAL(10, 2),
        default=0
    )

    lead_time_days: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    shortage_score: Mapped[float] = mapped_column(
        DECIMAL(5, 2)
    )

    severity: Mapped[SeverityEnum] = mapped_column(
        Enum(SeverityEnum),
        default=SeverityEnum.SAFE
    )

    last_restocked_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True)
    )

    facility = relationship(
        "Facility",
        back_populates="inventories"
    )

    medicine = relationship(
        "Medicine",
        back_populates="inventories"
    )

    batches = relationship(
        "InventoryBatch",
        back_populates="inventory"
    )


# =========================================================
# INVENTORY BATCH
# =========================================================

class InventoryBatch(Base, TimestampMixin):
    __tablename__ = "inventory_batches"

    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    inventory_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("inventory_current.inventory_id"),
        nullable=False
    )

    batch_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    supplier_name: Mapped[str] = mapped_column(
        String(255)
    )

    manufacturing_date: Mapped[str] = mapped_column(
        Date
    )

    expiry_date: Mapped[str] = mapped_column(
        Date,
        nullable=False
    )

    quantity_received: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    quantity_available: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    quantity_reserved: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    unit_cost: Mapped[float] = mapped_column(
        DECIMAL(10, 2)
    )

    inventory = relationship(
        "InventoryCurrent",
        back_populates="batches"
    )


# =========================================================
# INVENTORY SNAPSHOT
# =========================================================

class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"

    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    facility_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("facilities.facility_id")
    )

    medicine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("medicine_master.medicine_id")
    )

    total_stock: Mapped[int] = mapped_column(
        Integer
    )

    shortage_score: Mapped[float] = mapped_column(
        DECIMAL(5, 2)
    )

    severity: Mapped[SeverityEnum] = mapped_column(
        Enum(SeverityEnum)
    )

    snapshot_timestamp: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True)
    )
