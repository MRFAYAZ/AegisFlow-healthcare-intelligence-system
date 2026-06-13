from app.core.database import SessionLocal

from app.services.analytics.shortage_analytics_service import (
    ShortageAnalyticsService
)


def test_shortage_analytics():

    db = SessionLocal()

    try:

        analytics_service = (
            ShortageAnalyticsService(db)
        )

        snapshot = (
            analytics_service
            .get_shortage_analytics_snapshot()
        )

        print(snapshot)

        print(
            "✅ Shortage analytics working"
        )

    finally:
        db.close()


if __name__ == "__main__":
    test_shortage_analytics()