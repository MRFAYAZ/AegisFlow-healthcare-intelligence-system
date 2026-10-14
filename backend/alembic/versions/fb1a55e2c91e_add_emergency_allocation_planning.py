"""add emergency allocation planning

Revision ID: fb1a55e2c91e
Revises: 7ef82d0b9e1f
Create Date: 2026-09-09 00:07:25.362599
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "fb1a55e2c91e"
down_revision: Union[str, Sequence[str], None] = "7ef82d0b9e1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create emergency allocation planning tables only."""
    allocation_plan_status = sa.Enum(
        "DRAFT",
        "RECOMMENDED",
        "PENDING_APPROVAL",
        "PARTIALLY_APPROVED",
        "APPROVED",
        "PARTIALLY_FULFILLED",
        "FULFILLED",
        "FAILED",
        "CANCELLED",
        name="allocationplanstatusenum",
    )
    allocation_line_status = sa.Enum(
        "RECOMMENDED",
        "PENDING_APPROVAL",
        "APPROVED",
        "REJECTED",
        "PARTIALLY_FULFILLED",
        "FULFILLED",
        "FAILED",
        "CANCELLED",
        name="allocationlinestatusenum",
    )

    op.create_table(
        "emergency_allocation_plans",
        sa.Column("allocation_plan_id", sa.UUID(), nullable=False),
        sa.Column("emergency_case_id", sa.UUID(), nullable=False),
        sa.Column("medicine_id", sa.UUID(), nullable=False),
        sa.Column("requested_quantity", sa.Integer(), nullable=False),
        sa.Column("recommended_quantity", sa.Integer(), nullable=False),
        sa.Column("allocated_quantity", sa.Integer(), nullable=False),
        sa.Column("fulfillment_percentage", sa.DECIMAL(5, 2), nullable=False),
        sa.Column("optimization_score", sa.DECIMAL(8, 4), nullable=True),
        sa.Column("status", allocation_plan_status, nullable=False),
        sa.Column("recommendation_reason", sa.Text(), nullable=True),
        sa.Column("approved_by", sa.UUID(), nullable=True),
        sa.Column("approved_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["emergency_case_id"], ["emergency_cases.emergency_case_id"]),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicine_master.medicine_id"]),
        sa.PrimaryKeyConstraint("allocation_plan_id"),
        sa.UniqueConstraint("emergency_case_id"),
    )
    op.create_table(
        "emergency_allocation_lines",
        sa.Column("allocation_line_id", sa.UUID(), nullable=False),
        sa.Column("allocation_plan_id", sa.UUID(), nullable=False),
        sa.Column("source_facility_id", sa.UUID(), nullable=False),
        sa.Column("medicine_id", sa.UUID(), nullable=False),
        sa.Column("match_id", sa.UUID(), nullable=True),
        sa.Column("recommended_quantity", sa.Integer(), nullable=False),
        sa.Column("approved_quantity", sa.Integer(), nullable=False),
        sa.Column("source_available_quantity", sa.Integer(), nullable=False),
        sa.Column("source_safe_transferable_quantity", sa.Integer(), nullable=False),
        sa.Column("distance_km", sa.DECIMAL(10, 2), nullable=False),
        sa.Column("allocation_score", sa.DECIMAL(8, 4), nullable=False),
        sa.Column("allocation_reason", sa.Text(), nullable=True),
        sa.Column("status", allocation_line_status, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["allocation_plan_id"], ["emergency_allocation_plans.allocation_plan_id"]),
        sa.ForeignKeyConstraint(["match_id"], ["emergency_source_matches.match_id"]),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicine_master.medicine_id"]),
        sa.ForeignKeyConstraint(["source_facility_id"], ["facilities.facility_id"]),
        sa.PrimaryKeyConstraint("allocation_line_id"),
    )


def downgrade() -> None:
    """Remove emergency allocation planning tables only."""
    op.drop_table("emergency_allocation_lines")
    op.drop_table("emergency_allocation_plans")
