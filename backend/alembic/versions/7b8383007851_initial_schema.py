"""initial_schema

Revision ID: 7b8383007851
Revises:
Create Date: 2026-05-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql

from geoalchemy2 import Geography


# =========================================================
# REVISION IDENTIFIERS
# =========================================================

revision: str = "7b8383007851"

down_revision: Union[str, Sequence[str], None] = None

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


# =========================================================
# ENUM DEFINITIONS
# =========================================================

from sqlalchemy.dialects.postgresql import ENUM

facility_type_enum = ENUM(
    "HOSPITAL",
    "MEDICAL_SHOP",
    "SUPPLIER",
    "WAREHOUSE",
    name="facilitytypeenum",
    create_type=False
)

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

# =========================================================
# UPGRADE
# =========================================================

def upgrade() -> None:

    bind = op.get_bind()

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type
            WHERE typname = 'facilitytypeenum'
        ) THEN
            CREATE TYPE facilitytypeenum AS ENUM (
                'HOSPITAL',
                'MEDICAL_SHOP',
                'SUPPLIER',
                'WAREHOUSE'
            );
        END IF;
    END$$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type
            WHERE typname = 'severityenum'
        ) THEN
            CREATE TYPE severityenum AS ENUM (
                'SAFE',
                'WARNING',
                'CRITICAL',
                'EMERGENCY'
            );
        END IF;
    END$$;
    """)



    # =====================================================
    # LOCATIONS
    # =====================================================

    op.create_table(
        "locations",

        sa.Column(
            "location_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "country",
            sa.String(length=100),
            nullable=False,
            server_default=sa.text("'India'")
        ),

        sa.Column(
            "state",
            sa.String(length=100),
            nullable=False
        ),

        sa.Column(
            "district",
            sa.String(length=100),
            nullable=False
        ),

        sa.Column(
            "city",
            sa.String(length=100),
            nullable=False
        ),

        sa.Column(
            "postal_code",
            sa.String(length=20),
            nullable=False
        ),

        sa.Column(
            "address_line",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "latitude",
            sa.Numeric(10, 7),
            nullable=False
        ),

        sa.Column(
            "longitude",
            sa.Numeric(10, 7),
            nullable=False
        ),

        sa.Column(
            "geo_point",
            Geography(
                geometry_type="POINT",
                srid=4326
            ),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.CheckConstraint(
            "latitude BETWEEN -90 AND 90",
            name="ck_locations_latitude"
        ),

        sa.CheckConstraint(
            "longitude BETWEEN -180 AND 180",
            name="ck_locations_longitude"
        )
    )


    # =====================================================
    # MEDICINE MASTER
    # =====================================================

    op.create_table(
        "medicine_master",

        sa.Column(
            "medicine_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "medicine_code",
            sa.String(50),
            nullable=False,
            unique=True
        ),

        sa.Column(
            "medicine_name",
            sa.String(255),
            nullable=False
        ),

        sa.Column(
            "generic_name",
            sa.String(255),
            nullable=False
        ),

        sa.Column(
            "category",
            sa.String(100),
            nullable=False
        ),

        sa.Column(
            "dosage_form",
            sa.String(50),
            nullable=False
        ),

        sa.Column(
            "strength",
            sa.String(50),
            nullable=False
        ),

        sa.Column(
            "manufacturer",
            sa.String(255),
            nullable=False
        ),

        sa.Column(
            "prescription_required",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false")
        ),

        sa.Column(
            "is_critical",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false")
        ),

        sa.Column(
            "storage_conditions",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "standard_lead_time_days",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "safety_stock_days",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "unit_price",
            sa.Numeric(10, 2),
            nullable=False
        ),

        sa.Column(
            "expiry_alert_days",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.CheckConstraint(
            "unit_price >= 0",
            name="ck_medicine_unit_price"
        )
    )

    op.create_index(
        "idx_medicine_category",
        "medicine_master",
        ["category"]
    )

    # =====================================================
    # FACILITIES
    # =====================================================

    op.create_table(
        "facilities",

        sa.Column(
            "facility_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "facility_name",
            sa.String(255),
            nullable=False
        ),

        sa.Column(
            "facility_type",
            facility_type_enum,
            nullable=False
        ),

        sa.Column(
            "location_id",
            postgresql.UUID(as_uuid=True),

            sa.ForeignKey(
                "locations.location_id",
                ondelete="RESTRICT"
            ),

            nullable=False
        ),

        sa.Column(
            "license_number",
            sa.String(100),
            nullable=False,
            unique=True
        ),

        sa.Column(
            "contact_email",
            sa.String(255),
            nullable=False,
            unique=True
        ),

        sa.Column(
            "contact_phone",
            sa.String(20),
            nullable=False
        ),

        sa.Column(
            "emergency_contact",
            sa.String(20),
            nullable=False
        ),

        sa.Column(
            "is_24x7",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false")
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true")
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        )
    )

    op.create_index(
        "idx_facilities_type",
        "facilities",
        ["facility_type"]
    )

    # =====================================================
    # INVENTORY CURRENT
    # =====================================================

    op.create_table(
        "inventory_current",

        sa.Column(
            "inventory_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False
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
            "total_stock",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0")
        ),

        sa.Column(
            "available_stock",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0")
        ),

        sa.Column(
            "reserved_stock",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0")
        ),

        sa.Column(
            "minimum_threshold",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0")
        ),

        sa.Column(
            "reorder_threshold",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0")
        ),

        sa.Column(
            "daily_consumption_rate",
            sa.Numeric(10, 2),
            nullable=False,
            server_default=sa.text("0")
        ),

        sa.Column(
            "lead_time_days",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0")
        ),

        sa.Column(
            "shortage_score",
            sa.Numeric(5, 2),
            nullable=False,
            server_default=sa.text("0")
        ),

        sa.Column(
            "severity",
            severity_enum,
            nullable=False,
            server_default=sa.text("'SAFE'")
        ),

        sa.Column(
            "last_restocked_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.UniqueConstraint(
            "facility_id",
            "medicine_id",
            name="uq_inventory_facility_medicine"
        ),

        sa.CheckConstraint(
            "total_stock >= 0",
            name="ck_total_stock_positive"
        ),

        sa.CheckConstraint(
            "available_stock >= 0",
            name="ck_available_stock_positive"
        ),

        sa.CheckConstraint(
            "reserved_stock >= 0",
            name="ck_reserved_stock_positive"
        ),

        sa.CheckConstraint(
            "shortage_score >= 0",
            name="ck_shortage_score_positive"
        )
    )

    op.create_index(
        "idx_inventory_facility_medicine",
        "inventory_current",
        ["facility_id", "medicine_id"]
    )

    op.create_index(
        "idx_inventory_severity",
        "inventory_current",
        ["severity"]
    )

    # =====================================================
    # INVENTORY BATCHES
    # =====================================================

    op.create_table(
        "inventory_batches",

        sa.Column(
            "batch_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False
        ),

        sa.Column(
            "inventory_id",
            postgresql.UUID(as_uuid=True),

            sa.ForeignKey(
                "inventory_current.inventory_id",
                ondelete="CASCADE"
            ),

            nullable=False
        ),

        sa.Column(
            "batch_number",
            sa.String(100),
            nullable=False
        ),

        sa.Column(
            "supplier_name",
            sa.String(255),
            nullable=False
        ),

        sa.Column(
            "manufacturing_date",
            sa.Date(),
            nullable=False
        ),

        sa.Column(
            "expiry_date",
            sa.Date(),
            nullable=False
        ),

        sa.Column(
            "quantity_received",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0")
        ),

        sa.Column(
            "quantity_available",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0")
        ),

        sa.Column(
            "quantity_reserved",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0")
        ),

        sa.Column(
            "unit_cost",
            sa.Numeric(10, 2),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.CheckConstraint(
            "quantity_received >= 0",
            name="ck_quantity_received_positive"
        ),

        sa.CheckConstraint(
            "quantity_available >= 0",
            name="ck_quantity_available_positive"
        ),

        sa.CheckConstraint(
            "quantity_reserved >= 0",
            name="ck_quantity_reserved_positive"
        )
    )

    op.create_index(
        "idx_inventory_batches_expiry",
        "inventory_batches",
        ["expiry_date"]
    )


# =========================================================
# DOWNGRADE
# =========================================================

def downgrade() -> None:

    op.drop_index(
        "idx_inventory_batches_expiry",
        table_name="inventory_batches"
    )

    op.drop_table("inventory_batches")

    op.drop_index(
        "idx_inventory_severity",
        table_name="inventory_current"
    )

    op.drop_index(
        "idx_inventory_facility_medicine",
        table_name="inventory_current"
    )

    op.drop_table("inventory_current")

    op.drop_index(
        "idx_facilities_type",
        table_name="facilities"
    )

    op.drop_table("facilities")

    op.drop_index(
        "idx_medicine_category",
        table_name="medicine_master"
    )

    op.drop_table("medicine_master")


    op.drop_table("locations")
