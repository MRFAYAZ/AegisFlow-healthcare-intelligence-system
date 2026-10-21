"""add transfer decisions and dispatch lifecycle

Revision ID: c7f8a05d92b1
Revises: fa62ff385ef4
Create Date: 2026-10-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "c7f8a05d92b1"
down_revision: Union[str, Sequence[str], None] = "fa62ff385ef4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This guarded addition also repairs environments where emergency_case_id
    # was previously added manually and never recorded in Alembic.
    op.execute("""
    ALTER TABLE transfer_requests
    ADD COLUMN IF NOT EXISTS emergency_case_id UUID
    """)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint
            WHERE conname = 'fk_transfer_requests_emergency_case'
        ) THEN
            ALTER TABLE transfer_requests
            ADD CONSTRAINT fk_transfer_requests_emergency_case
            FOREIGN KEY (emergency_case_id)
            REFERENCES emergency_cases(emergency_case_id)
            ON DELETE SET NULL;
        END IF;
    END $$;
    """)
    op.execute("""
    ALTER TABLE transfer_requests
    ADD COLUMN IF NOT EXISTS requested_by UUID
    """)
    op.execute("""
    ALTER TABLE transfer_requests
    ADD COLUMN IF NOT EXISTS approved_by UUID
    """)
    op.execute("""
    ALTER TABLE transfer_requests
    ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP WITH TIME ZONE
    """)
    op.execute("""
    ALTER TABLE transfer_requests
    ADD COLUMN IF NOT EXISTS rejection_reason TEXT
    """)
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_transfer_emergency_case
    ON transfer_requests (emergency_case_id)
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'dispatchstatusenum'
        ) THEN
            CREATE TYPE dispatchstatusenum AS ENUM (
                'ASSIGNED', 'IN_TRANSIT', 'DELIVERED', 'FAILED', 'CANCELLED'
            );
        END IF;
    END $$;
    """)

    dispatch_status = postgresql.ENUM(
        "ASSIGNED", "IN_TRANSIT", "DELIVERED", "FAILED", "CANCELLED",
        name="dispatchstatusenum",
        create_type=False,
    )
    op.create_table(
        "transfer_dispatches",
        sa.Column("dispatch_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "transfer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("transfer_requests.transfer_id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("dispatcher_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("transport_type", sa.String(100), nullable=False),
        sa.Column("vehicle_reference", sa.String(100), nullable=True),
        sa.Column("status", dispatch_status, nullable=False),
        sa.Column("dispatched_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("estimated_arrival_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_dispatch_status", "transfer_dispatches", ["status"])


def downgrade() -> None:
    op.drop_index("idx_dispatch_status", table_name="transfer_dispatches")
    op.drop_table("transfer_dispatches")
    op.execute("DROP TYPE IF EXISTS dispatchstatusenum")
    op.execute("DROP INDEX IF EXISTS idx_transfer_emergency_case")
    op.drop_column("transfer_requests", "rejection_reason")
    op.drop_column("transfer_requests", "approved_at")
    op.drop_column("transfer_requests", "approved_by")
    op.drop_column("transfer_requests", "requested_by")
    # Keep emergency_case_id/FK because they may predate this migration in
    # installations where schema drift had already been repaired manually.
