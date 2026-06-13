from app.core.database import SessionLocal

from app.services.analytics.forecasting_service import (
    ForecastingService
)


def test_forecasting_service():

    db = SessionLocal()

    try:

        forecasting_service = (
            ForecastingService(db)
        )

        snapshot = (
            forecasting_service
            .get_forecasting_snapshot()
        )

        print(snapshot)

        print(
            "✅ Forecasting service working"
        )

    finally:
        db.close()


if __name__ == "__main__":
    test_forecasting_service()