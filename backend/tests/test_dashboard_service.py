from app.core.database import SessionLocal

from app.services.analytics.dashboard_service import (
    DashboardService
)


def test_dashboard_service():

    db = SessionLocal()

    try:

        dashboard_service = (
            DashboardService(db)
        )

        snapshot = (
            dashboard_service
            .get_dashboard_snapshot()
        )

        print(snapshot)

        print(
            "✅ Dashboard service working"
        )

    finally:
        db.close()


if __name__ == "__main__":
    test_dashboard_service()