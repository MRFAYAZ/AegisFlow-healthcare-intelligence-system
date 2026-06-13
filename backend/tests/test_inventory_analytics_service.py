from app.core.database import SessionLocal

from app.services.analytics.inventory_analytics_service import (
    InventoryAnalyticsService
)


def test_inventory_analytics():

    db = SessionLocal()

    try:

        analytics_service = (
            InventoryAnalyticsService(db)
        )

        snapshot = (
            analytics_service
            .get_inventory_analytics_snapshot()
        )

        print(snapshot)

        print(
            "✅ Inventory analytics working"
        )

    finally:
        db.close()


if __name__ == "__main__":
    test_inventory_analytics()