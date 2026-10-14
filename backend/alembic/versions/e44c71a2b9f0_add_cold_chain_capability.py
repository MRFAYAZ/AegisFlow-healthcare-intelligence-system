"""add explicit cold-chain requirements and facility capability

Revision ID: e44c71a2b9f0
Revises: d18c0a5e712f
Create Date: 2026-10-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e44c71a2b9f0"
down_revision: Union[str, Sequence[str], None] = "d18c0a5e712f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "medicine_master",
        sa.Column("requires_cold_chain", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "facilities",
        sa.Column("cold_chain_capable", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("facilities", "cold_chain_capable")
    op.drop_column("medicine_master", "requires_cold_chain")
