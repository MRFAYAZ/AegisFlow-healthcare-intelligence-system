"""add partner inventory integration gateway and idempotency receipts

Revision ID: a31d9f06c2b8
Revises: f6a91c73d840
Create Date: 2026-10-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a31d9f06c2b8"
down_revision: Union[str, Sequence[str], None] = "f6a91c73d840"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "integration_sources",
        sa.Column("source_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_name", sa.String(255), nullable=False),
        sa.Column("system_type", sa.String(80), nullable=False),
        sa.Column("facility_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("facilities.facility_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("credential_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("last_snapshot_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_integration_sources_facility", "integration_sources", ["facility_id"])

    op.create_table(
        "integration_medicine_mappings",
        sa.Column("mapping_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("integration_sources.source_id", ondelete="CASCADE"), nullable=False),
        sa.Column("external_medicine_code", sa.String(100), nullable=False),
        sa.Column("medicine_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("medicine_master.medicine_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("source_id", "external_medicine_code", name="uq_integration_medicine_source_external_code"),
    )
    op.create_index("idx_integration_mappings_source", "integration_medicine_mappings", ["source_id"])

    op.create_table(
        "integration_events",
        sa.Column("integration_event_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("integration_sources.source_id", ondelete="CASCADE"), nullable=False),
        sa.Column("external_event_id", sa.String(255), nullable=False),
        sa.Column("payload_hash", sa.String(64), nullable=False),
        sa.Column("source_timestamp", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("records_processed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("response_payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("received_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("processed_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.UniqueConstraint("source_id", "external_event_id", name="uq_integration_source_event"),
    )
    op.create_index("idx_integration_events_source_time", "integration_events", ["source_id", "source_timestamp"])


def downgrade() -> None:
    op.drop_index("idx_integration_events_source_time", table_name="integration_events")
    op.drop_table("integration_events")
    op.drop_index("idx_integration_mappings_source", table_name="integration_medicine_mappings")
    op.drop_table("integration_medicine_mappings")
    op.drop_index("idx_integration_sources_facility", table_name="integration_sources")
    op.drop_table("integration_sources")
