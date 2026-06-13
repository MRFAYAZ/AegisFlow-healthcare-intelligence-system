from sqlalchemy.orm import Session

from sqlalchemy import (
    func,
    select
)

from app.models.purchase import (
    PurchaseTransaction
)

from app.models.inventory import (
    InventoryCurrent
)

from app.models.medicine import (
    Medicine
)

from app.models.facility import (
    Facility
)


class ForecastingService:

    def __init__(self, db: Session):

        self.db = db

    # =====================================================
    # FORECAST MEDICINE DEMAND
    # =====================================================

    def forecast_medicine_demand(
        self,
        medicine_id
    ):

        avg_daily_consumption = (
            self.db.execute(
                select(
                    func.avg(
                        PurchaseTransaction.quantity
                    )
                )
                .where(
                    PurchaseTransaction.medicine_id
                    == medicine_id
                )
            )
            .scalar()
        )

        avg_daily_consumption = (
            avg_daily_consumption or 0
        )

        # ---------------------------------------------
        # SIMPLE 7-DAY FORECAST
        # ---------------------------------------------

        projected_weekly_demand = (
            avg_daily_consumption * 7
        )

        return {

            "medicine_id":
                str(medicine_id),

            "average_daily_consumption":
                round(
                    avg_daily_consumption,
                    2
                ),

            "projected_weekly_demand":
                round(
                    projected_weekly_demand,
                    2
                )
        }

    # =====================================================
    # PREDICT SHORTAGE RISK
    # =====================================================

    def predict_shortage_risk(
        self
    ):

        inventory_records = (
            self.db.execute(
                select(InventoryCurrent)
            )
            .scalars()
            .all()
        )

        predictions = []

        for inventory in inventory_records:

            # -----------------------------------------
            # PROJECTED CONSUMPTION
            # -----------------------------------------

            projected_consumption = (
                inventory.daily_consumption_rate
                * inventory.lead_time_days
            )

            # -----------------------------------------
            # SHORTAGE RISK
            # -----------------------------------------

            risk_probability = 0

            if (
                projected_consumption > 0
            ):

                risk_probability = (
                    projected_consumption
                    / max(
                        inventory.available_stock,
                        1
                    )
                ) * 100

            predictions.append({

                "inventory_id":
                    str(
                        inventory.inventory_id
                    ),

                "facility_id":
                    str(
                        inventory.facility_id
                    ),

                "medicine_id":
                    str(
                        inventory.medicine_id
                    ),

                "risk_probability":
                    round(
                        risk_probability,
                        2
                    )
            })

        return predictions

    # =====================================================
    # HIGH RISK FORECASTS
    # =====================================================

    def get_high_risk_forecasts(
        self,
        threshold: float = 80
    ):

        predictions = (
            self.predict_shortage_risk()
        )

        high_risk = [

            prediction

            for prediction in predictions

            if prediction[
                "risk_probability"
            ] >= threshold
        ]

        return high_risk

    # =====================================================
    # FACILITY DEMAND FORECAST
    # =====================================================

    def forecast_facility_demand(
        self,
        facility_id
    ):

        total_avg_consumption = (
            self.db.execute(
                select(
                    func.avg(
                        PurchaseTransaction.quantity
                    )
                )
                .where(
                    PurchaseTransaction.facility_id
                    == facility_id
                )
            )
            .scalar()
        )

        total_avg_consumption = (
            total_avg_consumption or 0
        )

        projected_monthly_demand = (
            total_avg_consumption * 30
        )

        return {

            "facility_id":
                str(facility_id),

            "average_daily_consumption":
                round(
                    total_avg_consumption,
                    2
                ),

            "projected_monthly_demand":
                round(
                    projected_monthly_demand,
                    2
                )
        }

    # =====================================================
    # FORECAST SNAPSHOT
    # =====================================================

    def get_forecasting_snapshot(
        self
    ):

        high_risk_forecasts = (
            self.get_high_risk_forecasts()
        )

        return {

            "high_risk_predictions":
                high_risk_forecasts,

            "total_high_risk_predictions":
                len(high_risk_forecasts)
        }