"""add procurement intelligence tables"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "20260909procurement"
down_revision: Union[str, Sequence[str], None] = "fb1a55e2c91e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    supply_status = sa.Enum(
        "PENDING_APPROVAL", "SENT", "ACCEPTED", "PARTIALLY_FULFILLED",
        "DECLINED", "FULFILLED", "CANCELLED", name="supplyrequeststatusenum",
    )
    priority = sa.Enum("SAFE", "WARNING", "CRITICAL", "EMERGENCY", name="severityenum", create_type=False)
    op.create_table(
        "replenishment_requirements",
        sa.Column("requirement_id", sa.UUID(), nullable=False),
        sa.Column("facility_id", sa.UUID(), nullable=False),
        sa.Column("medicine_id", sa.UUID(), nullable=False),
        sa.Column("requested_quantity", sa.Integer(), nullable=False),
        sa.Column("priority", priority, nullable=False),
        sa.Column("required_by", sa.TIMESTAMP(timezone=True)),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["facility_id"], ["facilities.facility_id"]),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicine_master.medicine_id"]),
        sa.PrimaryKeyConstraint("requirement_id"),
    )
    op.create_table(
        "supply_requests",
        sa.Column("request_id", sa.UUID(), nullable=False),
        sa.Column("requirement_id", sa.UUID(), nullable=False),
        sa.Column("supplier_facility_id", sa.UUID(), nullable=False),
        sa.Column("target_facility_id", sa.UUID(), nullable=False),
        sa.Column("medicine_id", sa.UUID(), nullable=False),
        sa.Column("requested_quantity", sa.Integer(), nullable=False),
        sa.Column("accepted_quantity", sa.Integer(), nullable=False),
        sa.Column("lead_time_days", sa.Integer(), nullable=False),
        sa.Column("recommendation_score", sa.DECIMAL(6, 2), nullable=False),
        sa.Column("status", supply_status, nullable=False),
        sa.Column("response_note", sa.Text()),
        sa.Column("responded_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["requirement_id"], ["replenishment_requirements.requirement_id"]),
        sa.ForeignKeyConstraint(["supplier_facility_id"], ["facilities.facility_id"]),
        sa.ForeignKeyConstraint(["target_facility_id"], ["facilities.facility_id"]),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicine_master.medicine_id"]),
        sa.PrimaryKeyConstraint("request_id"),
    )


def downgrade() -> None:
    op.drop_table("supply_requests")
    op.drop_table("replenishment_requirements")
    op.execute("DROP TYPE supplyrequeststatusenum")