"""add opt-in visibility and integration snapshot timestamps"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261014network"
down_revision: Union[str, Sequence[str], None] = "20260910merge"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "facilities",
        sa.Column(
            "network_visibility_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "inventory_current",
        sa.Column("external_observed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("inventory_current", "external_observed_at")
    op.drop_column("facilities", "network_visibility_enabled")