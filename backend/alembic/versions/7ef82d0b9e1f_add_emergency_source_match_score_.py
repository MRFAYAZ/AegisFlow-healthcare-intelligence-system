"""add emergency source match score components

Revision ID: 7ef82d0b9e1f
Revises: fa62ff385ef4
Create Date: 2026-09-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7ef82d0b9e1f"
down_revision: Union[str, Sequence[str], None] = "fa62ff385ef4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "emergency_source_matches",
        sa.Column(
            "distance_score",
            sa.Numeric(5, 4),
            nullable=True
        )
    )

    op.add_column(
        "emergency_source_matches",
        sa.Column(
            "inventory_score",
            sa.Numeric(5, 4),
            nullable=True
        )
    )

    op.add_column(
        "emergency_source_matches",
        sa.Column(
            "donor_health_score",
            sa.Numeric(5, 4),
            nullable=True
        )
    )


def downgrade() -> None:

    op.drop_column(
        "emergency_source_matches",
        "donor_health_score"
    )

    op.drop_column(
        "emergency_source_matches",
        "inventory_score"
    )

    op.drop_column(
        "emergency_source_matches",
        "distance_score"
    )