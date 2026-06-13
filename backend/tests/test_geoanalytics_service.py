from app.core.database import SessionLocal

from app.services.analytics.geoanalytics_service import (
    GeoAnalyticsService
)


def test_geoanalytics_service():

    db = SessionLocal()

    try:

        geo_service = (
            GeoAnalyticsService(db)
        )

        hotspots = (
            geo_service
            .get_geoanalytics_snapshot()
        )

        print(hotspots)

        nearest = (
            geo_service
            .find_nearest_facilities(
                latitude=17.3850,
                longitude=78.4867
            )
        )

        print(nearest)

        print(
            "✅ Geoanalytics working"
        )

    finally:
        db.close()


if __name__ == "__main__":
    test_geoanalytics_service()