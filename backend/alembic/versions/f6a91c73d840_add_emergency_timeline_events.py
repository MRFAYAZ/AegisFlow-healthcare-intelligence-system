"""add append-only emergency operational timeline events

Revision ID: f6a91c73d840
Revises: e44c71a2b9f0
Create Date: 2026-10-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "f6a91c73d840"
down_revision: Union[str, Sequence[str], None] = "e44c71a2b9f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "emergency_timeline_events",
        sa.Column("timeline_event_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "emergency_case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("emergency_cases.emergency_case_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "transfer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("transfer_requests.transfer_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column("event_payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("occurred_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_emergency_timeline_case_time",
        "emergency_timeline_events",
        ["emergency_case_id", "occurred_at"],
    )
    op.create_index(
        "idx_emergency_timeline_transfer",
        "emergency_timeline_events",
        ["transfer_id"],
    )
    # Make the event table append-only even if a later application bug issues
    # UPDATE or DELETE against it.
    op.execute("""
    CREATE OR REPLACE FUNCTION reject_emergency_timeline_event_mutation()
    RETURNS trigger AS $
    BEGIN
        RAISE EXCEPTION 'Emergency timeline events are append-only';
    END;
    $ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_emergency_timeline_events_append_only
    BEFORE UPDATE OR DELETE ON emergency_timeline_events
    FOR EACH ROW EXECUTE FUNCTION reject_emergency_timeline_event_mutation();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_emergency_timeline_events_append_only ON emergency_timeline_events")
    op.execute("DROP FUNCTION IF EXISTS reject_emergency_timeline_event_mutation()")
    op.drop_index("idx_emergency_timeline_transfer", table_name="emergency_timeline_events")
    op.drop_index("idx_emergency_timeline_case_time", table_name="emergency_timeline_events")
    op.drop_table("emergency_timeline_events")
