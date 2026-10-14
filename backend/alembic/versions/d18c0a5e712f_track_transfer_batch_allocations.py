"""track FEFO batch allocations for redistribution transfers

Revision ID: d18c0a5e712f
Revises: c7f8a05d92b1
Create Date: 2026-10-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "d18c0a5e712f"
down_revision: Union[str, Sequence[str], None] = "c7f8a05d92b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "transfer_batch_allocations",
        sa.Column("allocation_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "transfer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("transfer_requests.transfer_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "batch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("inventory_batches.batch_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("allocated_quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "allocated_quantity > 0",
            name="ck_transfer_batch_allocation_positive_quantity",
        ),
        sa.UniqueConstraint(
            "transfer_id",
            "batch_id",
            name="uq_transfer_batch_allocation_transfer_batch",
        ),
    )
    op.create_index(
        "idx_transfer_batch_allocation_transfer",
        "transfer_batch_allocations",
        ["transfer_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_transfer_batch_allocation_transfer", table_name="transfer_batch_allocations")
    op.drop_table("transfer_batch_allocations")
