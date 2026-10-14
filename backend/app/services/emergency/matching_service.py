from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engines.emergency.geo import haversine_km
from app.engines.emergency.matching_engine import MatchingEngine
from app.engines.inventory.medicine_safety import safe_transferable_quantity
from app.models.facility import Facility
from app.models.inventory import InventoryBatch, InventoryCurrent
from app.models.location import Location
from app.models.medicine import Medicine


class MatchingService:
    """Discover eligible, expiry-verified inventory and rank it explainably."""

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
        if requesting_location.latitude is None or requesting_location.longitude is None:
            raise ValueError("Requesting facility needs coordinates for geographic donor matching.")

        medicine = self.db.get(Medicine, medicine_id)
        if medicine is None:
            raise ValueError("Medicine was not found.")
        if medicine.requires_cold_chain and not requesting_facility.cold_chain_capable:
            return []

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
        if not rows:
            return []

        inventory_ids = [inventory.inventory_id for inventory, _, _ in rows]
        lots = self.db.execute(
            select(InventoryBatch)
            .where(InventoryBatch.inventory_id.in_(inventory_ids))
            .order_by(InventoryBatch.expiry_date.asc(), InventoryBatch.batch_id.asc())
        ).scalars().all()

        lots_by_inventory: dict[object, list[InventoryBatch]] = {}
        for lot in lots:
            lots_by_inventory.setdefault(lot.inventory_id, []).append(lot)

        today = date.today()
        candidates: list[dict] = []

        for inventory, facility, location in rows:
            # Cold-chain is a hard eligibility filter, not a ranking bonus.
            if medicine.requires_cold_chain and not facility.cold_chain_capable:
                continue

            # Batch traceability is a hard eligibility requirement in this
            # medicine-safety upgrade. An aggregate total alone cannot prove
            # that the stock is in date, so untracked stock is not offered.
            inventory_lots = lots_by_inventory.get(inventory.inventory_id, [])
            eligible_lots = [
                lot for lot in inventory_lots
                if lot.expiry_date is not None
                and lot.expiry_date >= today
                and int(lot.quantity_available or 0) > 0
            ]
            if not eligible_lots:
                continue

            batch_verified_quantity = sum(
                int(lot.quantity_available or 0) for lot in eligible_lots
            )
            aggregate_available_quantity = int(inventory.available_stock or 0)
            verified_available_quantity = min(
                aggregate_available_quantity,
                batch_verified_quantity,
            )
            transferable_quantity = safe_transferable_quantity(
                aggregate_available_stock=aggregate_available_quantity,
                minimum_threshold=int(inventory.minimum_threshold or 0),
                unexpired_batch_available=batch_verified_quantity,
            )
            if transferable_quantity <= 0:
                continue

            # Missing donor coordinates make this facility unrankable.
            # Exclude the candidate without aborting other available matches.
            if location.latitude is None or location.longitude is None:
                continue
            try:
                distance_km = haversine_km(
                    float(requesting_location.latitude),
                    float(requesting_location.longitude),
                    float(location.latitude),
                    float(location.longitude),
                )
            except (TypeError, ValueError):
                continue
            if max_distance_km is not None and distance_km > float(max_distance_km):
                continue

            candidates.append(
                {
                    "facility_id": str(facility.facility_id),
                    "facility_name": facility.facility_name,
                    "facility_type": facility.facility_type.value,
                    "requires_cold_chain": bool(medicine.requires_cold_chain),
                    "cold_chain_capable": bool(facility.cold_chain_capable),
                    "aggregate_available_quantity": aggregate_available_quantity,
                    "available_quantity": verified_available_quantity,
                    "transferable_quantity": transferable_quantity,
                    "suggested_quantity": min(transferable_quantity, requested_quantity),
                    "remaining_stock": verified_available_quantity,
                    "minimum_threshold": int(inventory.minimum_threshold or 0),
                    "distance_km": round(distance_km, 2),
                    "batch_traceability": "VERIFIED",
                    "eligible_batch_count": len(eligible_lots),
                    "nearest_expiry_date": min(lot.expiry_date for lot in eligible_lots).isoformat(),
                }
            )

        return MatchingEngine.generate_matches(candidates, requested_quantity)
