"""merge dispatch and safety migration heads"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260910merge"
down_revision: Union[str, Sequence[str], None] = ("7a69bb68aa65", "20260909safety")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass