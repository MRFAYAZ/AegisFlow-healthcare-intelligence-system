from app.core.database import SessionLocal

from app.services.analytics.consumption_analytics_service import (
    ConsumptionAnalyticsService
)


def test_consumption_analytics():

    db = SessionLocal()

    try:

        service = (
            ConsumptionAnalyticsService(db)
        )

        result = (
            service.get_consumption_snapshot()
        )

        print(result)

        print(
            "✅ Consumption Analytics Working"
        )

    finally:
        db.close()


if __name__ == "__main__":
    test_consumption_analytics()