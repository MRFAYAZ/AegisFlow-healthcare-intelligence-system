"""add user profile access records

Revision ID: 20261014_add_user_profiles
Revises: 20261014_add_network_exchange_controls
Create Date: 2026-10-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261014profile"
down_revision: Union[str, Sequence[str], None] = "20261014network"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("profile_id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_code", sa.String(length=80), nullable=False),
        sa.Column("profile_name", sa.String(length=120), nullable=False),
        sa.Column("module_access", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.UniqueConstraint("user_id", "profile_code", name="uq_user_profile_code"),
    )


def downgrade() -> None:
    op.drop_table("user_profiles")
