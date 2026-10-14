import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class TransferBatchAllocation(Base, TimestampMixin):
    """FEFO lot allocations reserved for a single transfer request."""

    __tablename__ = "transfer_batch_allocations"
    __table_args__ = (
        UniqueConstraint(
            "transfer_id",
            "batch_id",
            name="uq_transfer_batch_allocation_transfer_batch",
        ),
        CheckConstraint(
            "allocated_quantity > 0",
            name="ck_transfer_batch_allocation_positive_quantity",
        ),
    )

    allocation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    transfer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transfer_requests.transfer_id", ondelete="CASCADE"),
        nullable=False,
    )
    batch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("inventory_batches.batch_id", ondelete="RESTRICT"),
        nullable=False,
    )
    allocated_quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    transfer = relationship("TransferRequest", back_populates="batch_allocations")
    batch = relationship("InventoryBatch", back_populates="transfer_allocations")
