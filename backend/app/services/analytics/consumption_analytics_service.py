from sqlalchemy.orm import Session

from sqlalchemy import (
    func,
    select,
    desc
)

from app.models.purchase import (
    PurchaseTransaction
)

from app.models.medicine import (
    Medicine
)

from app.models.facility import (
    Facility
)


class ConsumptionAnalyticsService:

    def __init__(
        self,
        db: Session
    ):

        self.db = db

    # =====================================================
    # TOP CONSUMED MEDICINES
    # =====================================================

    def get_top_consumed_medicines(
        self,
        limit: int = 10
    ):

        results = (

            self.db.execute(

                select(

                    Medicine.medicine_name,

                    func.sum(
                        PurchaseTransaction.quantity
                    ).label(
                        "total_consumption"
                    )

                )

                .join(
                    PurchaseTransaction,
                    Medicine.medicine_id
                    ==
                    PurchaseTransaction.medicine_id
                )

                .group_by(
                    Medicine.medicine_name
                )

                .order_by(
                    desc(
                        "total_consumption"
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

                "total_consumption":
                    int(total_consumption)
            }

            for (
                medicine_name,
                total_consumption
            )

            in results

        ]

    # =====================================================
    # FACILITY CONSUMPTION
    # =====================================================

    def get_facility_consumption(
        self
    ):

        results = (

            self.db.execute(

                select(

                    Facility.facility_name,

                    func.sum(
                        PurchaseTransaction.quantity
                    ).label(
                        "total_consumption"
                    )

                )

                .join(
                    PurchaseTransaction,
                    Facility.facility_id
                    ==
                    PurchaseTransaction.facility_id
                )

                .group_by(
                    Facility.facility_name
                )

            )

            .all()

        )

        return [

            {
                "facility_name":
                    facility_name,

                "total_consumption":
                    int(total_consumption)
            }

            for (
                facility_name,
                total_consumption
            )

            in results

        ]

    # =====================================================
    # MEDICINE DEMAND TREND
    # =====================================================

    def get_medicine_demand_trend(
        self,
        medicine_id
    ):

        results = (

            self.db.execute(

                select(

                    func.date(
                        PurchaseTransaction.purchased_at
                    ).label(
                        "purchase_date"
                    ),

                    func.sum(
                        PurchaseTransaction.quantity
                    ).label(
                        "daily_consumption"
                    )

                )

                .where(
                    PurchaseTransaction.medicine_id
                    ==
                    medicine_id
                )

                .group_by(
                    func.date(
                        PurchaseTransaction.purchased_at
                    )
                )

                .order_by(
                    func.date(
                        PurchaseTransaction.purchased_at
                    )
                )

            )

            .all()

        )

        return [

            {
                "date":
                    str(date),

                "daily_consumption":
                    int(consumption)
            }

            for (
                date,
                consumption
            )

            in results

        ]

    # =====================================================
    # DEMAND SPIKE DETECTION
    # =====================================================

    def detect_demand_spikes(
        self
    ):

        medicines = (

            self.db.execute(
                select(Medicine)
            )

            .scalars()

            .all()

        )

        spikes = []

        for medicine in medicines:

            average_consumption = (

                self.db.execute(

                    select(
                        func.avg(
                            PurchaseTransaction.quantity
                        )
                    )

                    .where(
                        PurchaseTransaction.medicine_id
                        ==
                        medicine.medicine_id
                    )

                )

                .scalar()

            )

            total_consumption = (

                self.db.execute(

                    select(
                        func.sum(
                            PurchaseTransaction.quantity
                        )
                    )

                    .where(
                        PurchaseTransaction.medicine_id
                        ==
                        medicine.medicine_id
                    )

                )

                .scalar()

            )

            average_consumption = (
                average_consumption or 0
            )

            total_consumption = (
                total_consumption or 0
            )

            if (
                average_consumption > 0
                and
                total_consumption
                >
                average_consumption * 5
            ):

                spikes.append({

                    "medicine_id":
                        str(
                            medicine.medicine_id
                        ),

                    "medicine_name":
                        medicine.medicine_name,

                    "consumption_spike":
                        True

                })

        return spikes

    # =====================================================
    # ANALYTICS SNAPSHOT
    # =====================================================

    def get_consumption_snapshot(
        self
    ):

        return {

            "top_medicines":

                self
                .get_top_consumed_medicines(),

            "facility_consumption":

                self
                .get_facility_consumption(),

            "demand_spikes":

                self
                .detect_demand_spikes()

        }