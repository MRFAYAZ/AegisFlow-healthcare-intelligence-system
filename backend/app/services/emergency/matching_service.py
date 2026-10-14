from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engines.emergency.geo import haversine_km
from app.engines.emergency.matching_engine import MatchingEngine
from app.models.facility import Facility
from app.models.inventory import InventoryCurrent
from app.models.location import Location


class MatchingService:
    """Discover safe candidate inventories and rank them by explainable factors."""

    def __init__(self, db: Session):
        self.db = db

    def find_emergency_sources(
        self,
        medicine_id,
        requesting_facility_id,
        requested_quantity: int,
        max_distance_km: float | None = None,
    ) -> list[dict]:
        if requested_quantity <= 0:
            raise ValueError("Requested quantity must be greater than zero.")

        requesting_facility = self.db.get(Facility, requesting_facility_id)
        if requesting_facility is None:
            raise ValueError("Requesting facility was not found.")

        requesting_location = self.db.get(Location, requesting_facility.location_id)
        if requesting_location is None:
            raise ValueError("Requesting facility location was not found.")

        query = (
            select(InventoryCurrent, Facility, Location)
            .join(Facility, InventoryCurrent.facility_id == Facility.facility_id)
            .join(Location, Facility.location_id == Location.location_id)
            .where(
                InventoryCurrent.medicine_id == medicine_id,
                Facility.is_active.is_(True),
                InventoryCurrent.facility_id != requesting_facility_id,
            )
        )

        rows = self.db.execute(query).all()
        candidates: list[dict] = []

        for inventory, facility, location in rows:
            # available_stock represents unreserved usable stock in the current
            # inventory model. Protect the donor's minimum threshold.
            transferable_quantity = max(
                0, int(inventory.available_stock or 0)
                - int(inventory.minimum_threshold or 0)
            )
            if transferable_quantity <= 0:
                continue

            distance_km = haversine_km(
                float(requesting_location.latitude),
                float(requesting_location.longitude),
                float(location.latitude),
                float(location.longitude),
            )
            if max_distance_km is not None and distance_km > float(max_distance_km):
                continue

            candidates.append(
                {
                    "facility_id": str(facility.facility_id),
                    "facility_name": facility.facility_name,
                    "facility_type": facility.facility_type.value,
                    "available_quantity": transferable_quantity,
                    "transferable_quantity": transferable_quantity,
                    "suggested_quantity": min(
                        transferable_quantity, requested_quantity
                    ),
                    "remaining_stock": int(inventory.available_stock or 0),
                    "minimum_threshold": int(inventory.minimum_threshold or 0),
                    "distance_km": round(distance_km, 2),
                }
            )

        return MatchingEngine.generate_matches(candidates, requested_quantity)
