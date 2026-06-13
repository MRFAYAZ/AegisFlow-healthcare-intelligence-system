from sqlalchemy.orm import Session

from sqlalchemy import (
    func,
    select,
    desc
)

from app.models.inventory import (
    InventoryCurrent
)

from app.models.facility import (
    Facility
)

from app.models.medicine import (
    Medicine
)

from app.core.enums import (
    SeverityEnum
)


class ShortageAnalyticsService:

    def __init__(self, db: Session):

        self.db = db

    # =====================================================
    # OVERALL SHORTAGE PRESSURE
    # =====================================================

    def get_overall_shortage_pressure(
        self
    ):

        avg_shortage_score = (
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
            "overall_shortage_pressure":
                round(
                    avg_shortage_score or 0,
                    2
                )
        }

    # =====================================================
    # CRITICAL INVENTORY COUNT
    # =====================================================

    def get_critical_inventory_count(
        self
    ):

        critical_count = (
            self.db.execute(
                select(func.count())
                .where(
                    InventoryCurrent.severity.in_([
                        SeverityEnum.CRITICAL,
                        SeverityEnum.EMERGENCY
                    ])
                )
            )
            .scalar()
        )

        return {
            "critical_inventory_count":
                critical_count
        }

    # =====================================================
    # TOP HIGH-RISK FACILITIES
    # =====================================================

    def get_high_risk_facilities(
        self,
        limit: int = 10
    ):

        results = (
            self.db.execute(
                select(
                    Facility.facility_name,

                    func.avg(
                        InventoryCurrent.shortage_score
                    ).label(
                        "avg_shortage_score"
                    )
                )

                .join(
                    InventoryCurrent,
                    Facility.facility_id ==
                    InventoryCurrent.facility_id
                )

                .group_by(
                    Facility.facility_name
                )

                .order_by(
                    desc(
                        "avg_shortage_score"
                    )
                )

                .limit(limit)
            )
            .all()
        )

        return [
            {
                "facility_name":
                    facility_name,

                "average_shortage_score":
                    round(
                        avg_shortage_score or 0,
                        2
                    )
            }

            for (
                facility_name,
                avg_shortage_score
            ) in results
        ]

    # =====================================================
    # TOP HIGH-RISK MEDICINES
    # =====================================================

    def get_high_risk_medicines(
        self,
        limit: int = 10
    ):

        results = (
            self.db.execute(
                select(
                    Medicine.medicine_name,

                    func.avg(
                        InventoryCurrent.shortage_score
                    ).label(
                        "avg_shortage_score"
                    )
                )

                .join(
                    InventoryCurrent,
                    Medicine.medicine_id ==
                    InventoryCurrent.medicine_id
                )

                .group_by(
                    Medicine.medicine_name
                )

                .order_by(
                    desc(
                        "avg_shortage_score"
                    )
                )

                .limit(limit)
            )
            .all()
        )

        return [
            {
                "medicine_name":
                    medicine_name,

                "average_shortage_score":
                    round(
                        avg_shortage_score or 0,
                        2
                    )
            }

            for (
                medicine_name,
                avg_shortage_score
            ) in results
        ]

    # =====================================================
    # SEVERITY DISTRIBUTION
    # =====================================================

    def get_severity_distribution(
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
    # SHORTAGE ANALYTICS SNAPSHOT
    # =====================================================

    def get_shortage_analytics_snapshot(
        self
    ):

        return {

            "overall_shortage_pressure":
                self.get_overall_shortage_pressure(),

            "critical_inventory":
                self.get_critical_inventory_count(),

            "high_risk_facilities":
                self.get_high_risk_facilities(),

            "high_risk_medicines":
                self.get_high_risk_medicines(),

            "severity_distribution":
                self.get_severity_distribution()
        }