from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from sqlalchemy import (
    func,
    select
)

from app.models.inventory import (
    InventoryCurrent,
    InventoryBatch
)

from app.core.enums import (
    SeverityEnum
)


class InventoryAnalyticsService:

    def __init__(self, db: Session):

        self.db = db

    # =====================================================
    # INVENTORY SEVERITY DISTRIBUTION
    # =====================================================

    def get_inventory_severity_distribution(
        self
    ):

        results = (
            self.db.execute(
                select(
                    InventoryCurrent.severity,
                    func.count()
                )
                .group_by(
                    InventoryCurrent.severity
                )
            )
            .all()
        )

        return {
            str(severity): count
            for severity, count in results
        }

    # =====================================================
    # LOW STOCK INVENTORY COUNT
    # =====================================================

    def get_low_stock_count(self):

        count = (
            self.db.execute(
                select(func.count())
                .where(
                    InventoryCurrent.severity.in_([
                        SeverityEnum.WARNING,
                        SeverityEnum.CRITICAL,
                        SeverityEnum.EMERGENCY
                    ])
                )
            )
            .scalar()
        )

        return {
            "low_stock_inventory_count":
                count
        }

    # =====================================================
    # EXPIRING BATCHES
    # =====================================================

    def get_expiring_batches(
        self,
        days: int = 30
    ):

        expiry_threshold = (
            datetime.utcnow().date()
            + timedelta(days=days)
        )

        results = (
            self.db.execute(
                select(InventoryBatch)
                .where(
                    InventoryBatch.expiry_date
                    <= expiry_threshold
                )
            )
            .scalars()
            .all()
        )

        return results

    # =====================================================
    # AVERAGE SHORTAGE SCORE
    # =====================================================

    def get_average_shortage_score(
        self
    ):

        avg_score = (
            self.db.execute(
                select(
                    func.avg(
                        InventoryCurrent.shortage_score
                    )
                )
            )
            .scalar()
        )

        return {
            "average_shortage_score":
                round(avg_score or 0, 2)
        }

    # =====================================================
    # FACILITY INVENTORY HEALTH
    # =====================================================

    def get_facility_inventory_health(
        self
    ):

        results = (
            self.db.execute(
                select(
                    InventoryCurrent.facility_id,

                    func.avg(
                        InventoryCurrent.shortage_score
                    ).label(
                        "avg_shortage_score"
                    ),

                    func.count().label(
                        "inventory_count"
                    )
                )
                .group_by(
                    InventoryCurrent.facility_id
                )
            )
            .all()
        )

        return [
            {
                "facility_id":
                    facility_id,

                "average_shortage_score":
                    round(
                        avg_shortage_score or 0,
                        2
                    ),

                "inventory_count":
                    inventory_count
            }

            for (
                facility_id,
                avg_shortage_score,
                inventory_count
            ) in results
        ]

    # =====================================================
    # COMPLETE INVENTORY ANALYTICS
    # =====================================================

    def get_inventory_analytics_snapshot(
        self
    ):

        return {

            "severity_distribution":
                self.get_inventory_severity_distribution(),

            "low_stock_summary":
                self.get_low_stock_count(),

            "average_shortage":
                self.get_average_shortage_score(),

            "facility_health":
                self.get_facility_inventory_health()
        }