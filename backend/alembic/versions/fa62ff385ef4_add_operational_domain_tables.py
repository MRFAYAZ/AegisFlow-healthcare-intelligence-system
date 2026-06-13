"""add operational domain tables

Revision ID: fa62ff385ef4
Revises: 7b8383007851
Create Date: 2026-05-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM

revision: str = "fa62ff385ef4"
down_revision: Union[str, Sequence[str], None] = "7b8383007851"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# =====================================================
# ENUM DEFINITIONS
# =====================================================

severity_enum = ENUM(
    "SAFE",
    "WARNING",
    "CRITICAL",
    "EMERGENCY",
    name="severityenum",
    create_type=False
)

alert_status_enum = ENUM(
    "ACTIVE",
    "ACKNOWLEDGED",
    "RESOLVED",
    "EXPIRED",
    name="alertstatusenum",
    create_type=False
)

emergency_status_enum = ENUM(
    "ACTIVE",
    "MATCHING",
    "PARTIALLY_RESOLVED",
    "RESOLVED",
    "CLOSED",
    name="emergencystatusenum",
    create_type=False
)

purchase_status_enum = ENUM(
    "PENDING",
    "COMPLETED",
    "FAILED",
    "REFUNDED",
    name="purchasestatusenum",
    create_type=False
)

transfer_status_enum = ENUM(
    "PENDING",
    "APPROVED",
    "REJECTED",
    "IN_TRANSIT",
    "COMPLETED",
    "CANCELLED",
    name="transferstatusenum",
    create_type=False
)

def upgrade() -> None:

    # =====================================================
    # ENUMS
    # =====================================================

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM pg_type
            WHERE typname = 'alertstatusenum'
        ) THEN
            CREATE TYPE alertstatusenum AS ENUM (
                'ACTIVE',
                'ACKNOWLEDGED',
                'RESOLVED',
                'EXPIRED'
            );
        END IF;
    END$$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM pg_type
            WHERE typname = 'emergencystatusenum'
        ) THEN
            CREATE TYPE emergencystatusenum AS ENUM (
                'ACTIVE',
                'MATCHING',
                'PARTIALLY_RESOLVED',
                'RESOLVED',
                'CLOSED'
            );
        END IF;
    END$$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM pg_type
            WHERE typname = 'purchasestatusenum'
        ) THEN
            CREATE TYPE purchasestatusenum AS ENUM (
                'PENDING',
                'COMPLETED',
                'FAILED',
                'REFUNDED'
            );
        END IF;
    END$$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM pg_type
            WHERE typname = 'transferstatusenum'
        ) THEN
            CREATE TYPE transferstatusenum AS ENUM (
                'PENDING',
                'APPROVED',
                'REJECTED',
                'IN_TRANSIT',
                'COMPLETED',
                'CANCELLED'
            );
        END IF;
    END$$;
    """)

    # =====================================================
    # PURCHASE TRANSACTIONS
    # =====================================================

    op.create_table(
        "purchase_transactions",

        sa.Column(
            "purchase_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True
        ),

        sa.Column(
            "facility_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "facilities.facility_id",
                ondelete="RESTRICT"
            ),
            nullable=False
        ),

        sa.Column(
            "medicine_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "medicine_master.medicine_id",
                ondelete="RESTRICT"
            ),
            nullable=False
        ),

        sa.Column(
            "customer_name",
            sa.String(255)
        ),

        sa.Column(
            "customer_phone",
            sa.String(20)
        ),

        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "unit_price",
            sa.Numeric(10, 2),
            nullable=False
        ),

        sa.Column(
            "total_amount",
            sa.Numeric(10, 2),
            nullable=False
        ),

        sa.Column(
            "purchase_status",
            purchase_status_enum,
            nullable=False
        ),

        sa.Column(
            "stock_reduced",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false")
        ),

        sa.Column(
            "purchased_at",
            sa.TIMESTAMP(timezone=True)
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()")
        ),

        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()")
        )
    )

    # =====================================================
    # ALERT EVENTS
    # =====================================================

    op.create_table(
        "alert_events",

        sa.Column(
            "alert_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True
        ),

        sa.Column(
            "facility_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("facilities.facility_id"),
            nullable=False
        ),

        sa.Column(
            "medicine_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("medicine_master.medicine_id"),
            nullable=False
        ),

        sa.Column(
            "alert_type",
            sa.String(100),
            nullable=False
        ),

        sa.Column(
            "severity",
            severity_enum,
            nullable=False
        ),

        sa.Column(
            "alert_message",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "alert_status",
            alert_status_enum,
            nullable=False
        ),

        sa.Column(
            "triggered_at",
            sa.TIMESTAMP(timezone=True)
        ),

        sa.Column(
            "resolved_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()")
        ),

        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()")
        )
    )

    # =====================================================
    # EMERGENCY CASES
    # =====================================================

    op.create_table(
        "emergency_cases",

        sa.Column(
            "emergency_case_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True
        ),

        sa.Column(
            "facility_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("facilities.facility_id"),
            nullable=False
        ),

        sa.Column(
            "medicine_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("medicine_master.medicine_id"),
            nullable=False
        ),

        sa.Column(
            "shortage_score",
            sa.Numeric(5, 2),
            nullable=False
        ),

        sa.Column(
            "severity",
            severity_enum,
            nullable=False
        ),

        sa.Column(
            "emergency_radius_km",
            sa.Integer(),
            nullable=False,
            server_default="5"
        ),

        sa.Column(
            "required_quantity",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "available_quantity",
            sa.Integer(),
            nullable=False,
            server_default="0"
        ),

        sa.Column(
            "emergency_status",
            emergency_status_enum,
            nullable=False
        ),

        sa.Column(
            "triggered_at",
            sa.TIMESTAMP(timezone=True)
        ),

        sa.Column(
            "resolved_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()")
        ),

        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()")
        )
    )

    # =====================================================
    # EMERGENCY SOURCE MATCHES
    # =====================================================

    op.create_table(
        "emergency_source_matches",

        sa.Column(
            "match_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True
        ),

        sa.Column(
            "emergency_case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "emergency_cases.emergency_case_id",
                ondelete="CASCADE"
            ),
            nullable=False
        ),

        sa.Column(
            "source_facility_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("facilities.facility_id"),
            nullable=False
        ),

        sa.Column(
            "medicine_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("medicine_master.medicine_id"),
            nullable=False
        ),

        sa.Column(
            "available_quantity",
            sa.Integer()
        ),

        sa.Column(
            "transferable_quantity",
            sa.Integer()
        ),

        sa.Column(
            "distance_km",
            sa.Numeric(10, 2)
        ),

        sa.Column(
            "ranking_score",
            sa.Numeric(5, 2)
        ),

        sa.Column(
            "is_selected",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false")
        ),

        sa.Column(
            "matched_at",
            sa.TIMESTAMP(timezone=True)
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()")
        ),

        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()")
        )
    )

    # =====================================================
    # TRANSFER REQUESTS
    # =====================================================

    op.create_table(
        "transfer_requests",

        sa.Column(
            "transfer_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True
        ),

        sa.Column(
            "from_facility_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("facilities.facility_id"),
            nullable=False
        ),

        sa.Column(
            "to_facility_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("facilities.facility_id"),
            nullable=False
        ),

        sa.Column(
            "medicine_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("medicine_master.medicine_id"),
            nullable=False
        ),

        sa.Column(
            "requested_quantity",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "approved_quantity",
            sa.Integer()
        ),

        sa.Column(
            "transfer_status",
            transfer_status_enum,
            nullable=False
        ),

        sa.Column(
            "cascade_safe",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true")
        ),

        sa.Column(
            "match_score",
            sa.Numeric(5, 2)
        ),

        sa.Column(
            "transfer_distance_km",
            sa.Numeric(10, 2)
        ),

        sa.Column(
            "recommendation_reason",
            sa.Text()
        ),

        sa.Column(
            "requested_at",
            sa.TIMESTAMP(timezone=True)
        ),

        sa.Column(
            "completed_at",
            sa.TIMESTAMP(timezone=True)
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()")
        ),

        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()")
        )
    )

    # =====================================================
    # INVENTORY SNAPSHOTS
    # =====================================================

    op.create_table(
        "inventory_snapshots",

        sa.Column(
            "snapshot_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True
        ),

        sa.Column(
            "facility_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("facilities.facility_id")
        ),

        sa.Column(
            "medicine_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("medicine_master.medicine_id")
        ),

        sa.Column(
            "total_stock",
            sa.Integer()
        ),

        sa.Column(
            "shortage_score",
            sa.Numeric(5, 2)
        ),

        sa.Column(
            "severity",
            severity_enum
        ),

        sa.Column(
            "snapshot_timestamp",
            sa.TIMESTAMP(timezone=True)
        )
    )

    # =====================================================
    # INDEXES
    # =====================================================

    op.create_index(
        "idx_purchase_facility",
        "purchase_transactions",
        ["facility_id"]
    )

    op.create_index(
        "idx_purchase_medicine",
        "purchase_transactions",
        ["medicine_id"]
    )

    op.create_index(
        "idx_alert_status",
        "alert_events",
        ["alert_status"]
    )

    op.create_index(
        "idx_emergency_status",
        "emergency_cases",
        ["emergency_status"]
    )

    op.create_index(
        "idx_match_emergency",
        "emergency_source_matches",
        ["emergency_case_id"]
    )

    op.create_index(
        "idx_transfer_status",
        "transfer_requests",
        ["transfer_status"]
    )

    op.create_index(
        "idx_snapshot_timestamp",
        "inventory_snapshots",
        ["snapshot_timestamp"]
    )


def downgrade() -> None:

    op.drop_index("idx_snapshot_timestamp")
    op.drop_index("idx_transfer_status")
    op.drop_index("idx_match_emergency")
    op.drop_index("idx_emergency_status")
    op.drop_index("idx_alert_status")
    op.drop_index("idx_purchase_medicine")
    op.drop_index("idx_purchase_facility")

    op.drop_table("inventory_snapshots")
    op.drop_table("transfer_requests")
    op.drop_table("emergency_source_matches")
    op.drop_table("emergency_cases")
    op.drop_table("alert_events")
    op.drop_table("purchase_transactions")