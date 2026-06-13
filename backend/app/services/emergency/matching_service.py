from sqlalchemy.orm import Session

from app.repositories.inventory_repository import (
    InventoryRepository
)

from app.repositories.facility_repository import (
    FacilityRepository
)

from app.engines.emergency.matching_engine import (
    MatchingEngine
)


class MatchingService:

    def __init__(self, db: Session):

        self.db = db

        self.inventory_repository = (
            InventoryRepository(db)
        )

        self.facility_repository = (
            FacilityRepository(db)
        )

    # =====================================================
    # FIND EMERGENCY SOURCES
    # =====================================================

    def find_emergency_sources(
        self,
        medicine_id,
        requesting_facility_id,
        requested_quantity
    ):

        inventories = (
            self.inventory_repository
            .get_inventory_by_medicine(
                medicine_id
            )
        )

        candidates = []

        for inventory in inventories:

            if (
                inventory.facility_id
                == requesting_facility_id
            ):
                continue

            transferable_quantity = max(
                0,
                inventory.available_stock
                -
                inventory.minimum_threshold
            )

            if (
                transferable_quantity
                <= 0
            ):
                continue

            candidate = {

                "facility_id":
                    str(
                        inventory.facility_id
                    ),

                "available_quantity":
                    transferable_quantity,

                "remaining_stock":
                    inventory.available_stock,

                "minimum_threshold":
                    inventory.minimum_threshold,

                # temporary placeholder

                "distance_km": 10
            }

            candidates.append(
                candidate
            )

        ranked_candidates = (
            MatchingEngine
            .generate_matches(
                candidates,
                requested_quantity
            )
        )

        return ranked_candidates