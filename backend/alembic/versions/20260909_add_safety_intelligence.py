"""add batch, cold-chain, and emergency safety fields"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "20260909safety"
down_revision: Union[str, Sequence[str], None] = "20260909procurement"
branch_labels = None
depends_on = None


def upgrade() -> None:
    batch_status = sa.Enum(
        "AVAILABLE", "RESERVED", "QUARANTINED", "EXPIRED", "DAMAGED", "RECALLED", "DEPLETED",
        name="batchstatusenum",
    )
    batch_status.create(op.get_bind(), checkfirst=True)
    op.add_column("medicine_master", sa.Column("cold_chain_required", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("medicine_master", sa.Column("storage_min_celsius", sa.DECIMAL(5, 2)))
    op.add_column("medicine_master", sa.Column("storage_max_celsius", sa.DECIMAL(5, 2)))
    op.add_column("medicine_master", sa.Column("transport_requirement", sa.String(length=100)))
    op.add_column("facilities", sa.Column("cold_chain_capable", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("inventory_batches", sa.Column("status", batch_status, nullable=False, server_default="AVAILABLE"))
    op.add_column("emergency_source_matches", sa.Column("selected_batch_number", sa.String(length=100)))
    op.add_column("emergency_source_matches", sa.Column("earliest_expiry_date", sa.Date()))
    op.add_column("emergency_source_matches", sa.Column("cold_chain_required", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("emergency_source_matches", sa.Column("cold_chain_capable", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("emergency_source_matches", sa.Column("safety_status", sa.String(length=40), nullable=False, server_default="LEGACY_UNVALIDATED"))
    op.add_column("emergency_source_matches", sa.Column("safety_reason", sa.Text()))
    op.add_column("emergency_source_matches", sa.Column("batch_allocations", sa.JSON()))


def downgrade() -> None:
    for column in ("batch_allocations", "safety_reason", "safety_status", "cold_chain_capable", "cold_chain_required", "earliest_expiry_date", "selected_batch_number"):
        op.drop_column("emergency_source_matches", column)
    op.drop_column("inventory_batches", "status")
    op.drop_column("facilities", "cold_chain_capable")
    for column in ("transport_requirement", "storage_max_celsius", "storage_min_celsius", "cold_chain_required"):
        op.drop_column("medicine_master", column)
    op.execute("DROP TYPE batchstatusenum")