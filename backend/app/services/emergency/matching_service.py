from datetime import date

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

from app.utils.distance import (
    calculate_distance_km
)
from app.core.enums import BatchStatusEnum


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

        requesting_facility = (
            self.facility_repository.get_by_id(
                requesting_facility_id
            )
        )

        if not requesting_facility:
            raise ValueError(
                "Requesting facility not found."
            )

        if not requesting_facility.location:
            raise ValueError(
                "Requesting facility location not found."
            )

        requesting_latitude = (
            requesting_facility.location.latitude
        )

        requesting_longitude = (
            requesting_facility.location.longitude
        )

        inventories = (
            self.inventory_repository
            .get_inventory_by_medicine(
                medicine_id
            )
        )

        candidates = []

        for inventory in inventories:

            # -------------------------------------------------
            # Never match a facility with itself
            # -------------------------------------------------

            if (
                inventory.facility_id
                == requesting_facility_id
            ):
                continue

            # -------------------------------------------------
            # Get donor facility
            # -------------------------------------------------

            donor_facility = (
                self.facility_repository.get_by_id(
                    inventory.facility_id
                )
            )

            if not donor_facility:
                continue

            if not donor_facility.is_active:
                continue

            if not donor_facility.location:
                continue

            cold_chain_required = bool(inventory.medicine.cold_chain_required)
            cold_chain_capable = bool(donor_facility.cold_chain_capable)
            if cold_chain_required and not cold_chain_capable:
                continue

            eligible_batches = sorted(
                [
                    batch for batch in inventory.batches
                    if batch.status == BatchStatusEnum.AVAILABLE
                    and batch.expiry_date >= date.today()
                    and int(batch.quantity_available or 0) > 0
                ],
                key=lambda batch: batch.expiry_date,
            )

            if eligible_batches:
                safe_available_quantity = sum(
                    int(batch.quantity_available or 0)
                    for batch in eligible_batches
                )
                selected_batch_number = eligible_batches[0].batch_number
                earliest_expiry_date = eligible_batches[0].expiry_date
                safety_status = "PASSED"
                safety_reason = "Eligible batches passed status and expiry checks; FEFO order applied."
                remaining_quantity = max(
                    safe_available_quantity - int(inventory.minimum_threshold or 0),
                    0,
                )
                batch_allocations = []
                for batch in eligible_batches:
                    allocation_quantity = min(
                        int(batch.quantity_available or 0),
                        remaining_quantity,
                    )
                    if allocation_quantity > 0:
                        batch_allocations.append({
                            "batch_number": batch.batch_number,
                            "quantity": allocation_quantity,
                            "expiry_date": batch.expiry_date.isoformat(),
                        })
                        remaining_quantity -= allocation_quantity
                    if remaining_quantity <= 0:
                        break
            else:
                # Preserve compatibility for legacy inventory rows that predate batch tracking.
                safe_available_quantity = max(int(inventory.available_stock or 0), 0)
                selected_batch_number = None
                earliest_expiry_date = None
                safety_status = "LEGACY_UNVALIDATED"
                safety_reason = "No batch records available; legacy inventory quantity used."
                batch_allocations = []

            transferable_quantity = max(
                0,
                safe_available_quantity - int(inventory.minimum_threshold or 0)
            )

            if transferable_quantity <= 0:
                continue

            # -------------------------------------------------
            # Calculate real geographic distance
            # -------------------------------------------------

            distance_km = calculate_distance_km(
                requesting_latitude,
                requesting_longitude,
                donor_facility.location.latitude,
                donor_facility.location.longitude
            )

            # -------------------------------------------------
            # Build candidate
            # -------------------------------------------------

            candidate = {

                "facility_id":
                    inventory.facility_id,

                "available_quantity": (
                    transferable_quantity
                ),

                "remaining_stock": (
                    safe_available_quantity
                ),

                "minimum_threshold": (
                    inventory.minimum_threshold
                ),

                "distance_km": distance_km,
                "selected_batch_number": selected_batch_number,
                "earliest_expiry_date": earliest_expiry_date,
                "cold_chain_required": cold_chain_required,
                "cold_chain_capable": cold_chain_capable,
                "safety_status": safety_status,
                "safety_reason": safety_reason,
                "batch_allocations": batch_allocations,
            }

            candidates.append(candidate)

        # -----------------------------------------------------
        # Rank candidates
        # -----------------------------------------------------

        ranked_candidates = (
            MatchingEngine.generate_matches(
                candidates,
                requested_quantity
            )
        )

        return ranked_candidates