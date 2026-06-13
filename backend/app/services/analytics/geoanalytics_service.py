from sqlalchemy.orm import Session

from sqlalchemy import (
    text,
    select,
    func
)

from app.models.location import (
    Location
)

from app.models.facility import (
    Facility
)

from app.models.inventory import (
    InventoryCurrent
)

from app.core.enums import (
    SeverityEnum
)


class GeoAnalyticsService:

    def __init__(self, db: Session):

        self.db = db

    # =====================================================
    # FIND FACILITIES WITHIN RADIUS
    # =====================================================

    def find_facilities_within_radius(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10
    ):

        radius_meters = radius_km * 1000

        query = text(
            """
            SELECT
                f.facility_id,
                f.facility_name,
                l.city,

                ST_Distance(
                    l.geo_point,
                    ST_SetSRID(
                        ST_MakePoint(
                            :longitude,
                            :latitude
                        ),
                        4326
                    )::geography
                ) / 1000 AS distance_km

            FROM facilities f

            JOIN locations l
            ON f.location_id = l.location_id

            WHERE ST_DWithin(
                l.geo_point,

                ST_SetSRID(
                    ST_MakePoint(
                        :longitude,
                        :latitude
                    ),
                    4326
                )::geography,

                :radius_meters
            )

            ORDER BY distance_km ASC
            """
        )

        results = (
            self.db.execute(
                query,
                {
                    "latitude": latitude,
                    "longitude": longitude,
                    "radius_meters": radius_meters
                }
            )
            .mappings()
            .all()
        )

        return [
            dict(row)
            for row in results
        ]

    # =====================================================
    # FIND CRITICAL SHORTAGE HOTSPOTS
    # =====================================================

    def get_critical_shortage_hotspots(
        self
    ):

        query = (
            select(
                Facility.facility_name,

                Location.city,

                func.avg(
                    InventoryCurrent.shortage_score
                ).label(
                    "avg_shortage_score"
                )
            )

            .join(
                Location,
                Facility.location_id ==
                Location.location_id
            )

            .join(
                InventoryCurrent,
                Facility.facility_id ==
                InventoryCurrent.facility_id
            )

            .where(
                InventoryCurrent.severity.in_([
                    SeverityEnum.CRITICAL,
                    SeverityEnum.EMERGENCY
                ])
            )

            .group_by(
                Facility.facility_name,
                Location.city
            )

            .order_by(
                func.avg(
                    InventoryCurrent.shortage_score
                ).desc()
            )
        )

        results = (
            self.db.execute(query)
            .all()
        )

        return [
            {
                "facility_name":
                    facility_name,

                "city":
                    city,

                "average_shortage_score":
                    round(
                        avg_shortage_score or 0,
                        2
                    )
            }

            for (
                facility_name,
                city,
                avg_shortage_score
            ) in results
        ]

    # =====================================================
    # FIND NEAREST FACILITIES
    # =====================================================

    def find_nearest_facilities(
        self,
        latitude: float,
        longitude: float,
        limit: int = 5
    ):

        query = text(
            """
            SELECT
                f.facility_id,
                f.facility_name,
                l.city,

                ST_Distance(
                    l.geo_point,

                    ST_SetSRID(
                        ST_MakePoint(
                            :longitude,
                            :latitude
                        ),
                        4326
                    )::geography

                ) / 1000 AS distance_km

            FROM facilities f

            JOIN locations l
            ON f.location_id = l.location_id

            ORDER BY distance_km ASC

            LIMIT :limit
            """
        )

        results = (
            self.db.execute(
                query,
                {
                    "latitude": latitude,
                    "longitude": longitude,
                    "limit": limit
                }
            )
            .mappings()
            .all()
        )

        return [
            dict(row)
            for row in results
        ]

    # =====================================================
    # COMPLETE GEO ANALYTICS SNAPSHOT
    # =====================================================

    def get_geoanalytics_snapshot(
        self
    ):

        return {

            "critical_hotspots":
                self.get_critical_shortage_hotspots()
        }