from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from math import asin, cos, radians, sin, sqrt
from uuid import UUID

from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.enums import BatchStatusEnum, UserRoleEnum
from app.models.facility import Facility
from app.models.facility_user import FacilityUser
from app.models.inventory import InventoryCurrent
from app.models.medicine import Medicine
from app.models.user import User
from app.services.governance.audit_service import AuditService
from app.services.inventory.shortage_service import ShortageService


class NetworkExchangeService:
    """Publish controlled availability signals and rank eligible sources."""

    MAX_SNAPSHOT_AGE = timedelta(hours=24)
    MAX_CLOCK_SKEW = timedelta(minutes=5)

    def __init__(self, db: Session):
        self.db = db

    def update_availability(
        self,
        facility_id: UUID,
        snapshot,
        actor: User,
    ) -> InventoryCurrent:
        now = datetime.now(timezone.utc)
        if snapshot.observed_at < now - self.MAX_SNAPSHOT_AGE:
            raise ValueError("Snapshot is older than the 24-hour freshness window.")
        if snapshot.observed_at > now + self.MAX_CLOCK_SKEW:
            raise ValueError("Snapshot timestamp exceeds the allowed clock skew.")

        facility = self.db.query(Facility).filter(
            Facility.facility_id == facility_id,
            Facility.is_active.is_(True),
        ).first()
        if facility is None:
            raise ValueError("Active facility not found.")
        self._require_facility_access(facility_id, actor)

        medicine = self.db.query(Medicine).filter(
            Medicine.medicine_id == snapshot.medicine_id,
        ).first()
        if medicine is None:
            raise ValueError("Medicine not found.")

        inventory = (
            self.db.query(InventoryCurrent)
            .filter(
                InventoryCurrent.facility_id == facility_id,
                InventoryCurrent.medicine_id == snapshot.medicine_id,
            )
            .with_for_update()
            .first()
        )
        if inventory is not None and inventory.external_observed_at is not None:
            if snapshot.observed_at <= inventory.external_observed_at:
                raise ValueError("Snapshot is stale or has already been applied.")

        shortage_score = ShortageService.calculate_shortage_score(
            available_stock=snapshot.available_stock,
            daily_consumption_rate=(
                float(inventory.daily_consumption_rate or 0)
                if inventory is not None
                else 0
            ),
            lead_time_days=inventory.lead_time_days if inventory is not None else 0,
            safety_stock_days=7,
        )

        values = {
            "facility_id": facility_id,
            "medicine_id": snapshot.medicine_id,
            "total_stock": snapshot.total_stock,
            "available_stock": snapshot.available_stock,
            "reserved_stock": snapshot.reserved_stock,
            "minimum_threshold": snapshot.minimum_threshold,
            "shortage_score": shortage_score,
            "severity": ShortageService.determine_severity(shortage_score),
            "external_observed_at": snapshot.observed_at,
        }
        if inventory is None:
            inventory = InventoryCurrent(**values)
            self.db.add(inventory)
        else:
            for field, value in values.items():
                setattr(inventory, field, value)

        AuditService(self.db).record_event(
            action_type="INTEGRATION_AVAILABILITY_SYNCED",
            entity_type="FACILITY",
            entity_id=facility_id,
            user_id=actor.user_id,
            new_value={
                "medicine_id": str(snapshot.medicine_id),
                "source_system": snapshot.source_system,
                "observed_at": snapshot.observed_at.isoformat(),
            },
        )
        self.db.flush()
        return inventory

    def get_accessible_facilities(self, actor: User) -> list[Facility]:
        query = self.db.query(Facility).filter(Facility.is_active.is_(True))
        if UserRoleEnum(actor.role) != UserRoleEnum.SYSTEM_ADMIN:
            query = query.join(
                FacilityUser,
                FacilityUser.facility_id == Facility.facility_id,
            ).filter(FacilityUser.user_id == actor.user_id)
        return query.order_by(Facility.facility_name.asc()).all()

    def set_visibility(
        self,
        facility_id: UUID,
        enabled: bool,
        actor: User,
    ) -> Facility:
        facility = self.db.query(Facility).filter(
            Facility.facility_id == facility_id,
            Facility.is_active.is_(True),
        ).with_for_update().first()
        if facility is None:
            raise ValueError("Active facility not found.")
        self._require_facility_access(facility_id, actor)
        old_value = facility.network_visibility_enabled
        facility.network_visibility_enabled = enabled
        AuditService(self.db).record_event(
            action_type="NETWORK_VISIBILITY_UPDATED",
            entity_type="FACILITY",
            entity_id=facility_id,
            user_id=actor.user_id,
            old_value={"enabled": old_value},
            new_value={"enabled": enabled},
        )
        self.db.flush()
        return facility

    def search_offers(
        self,
        requester_facility_id: UUID,
        medicine_id: UUID,
        required_quantity: int,
        radius_km: float,
        emergency_override: bool,
        actor: User,
    ) -> list[dict]:
        requester = (
            self.db.query(Facility)
            .options(joinedload(Facility.location))
            .filter(
                Facility.facility_id == requester_facility_id,
                Facility.is_active.is_(True),
            )
            .first()
        )
        if requester is None:
            raise ValueError("Active requester facility not found.")
        self._require_facility_access(requester_facility_id, actor)

        medicine = self.db.query(Medicine).filter(
            Medicine.medicine_id == medicine_id,
        ).first()
        if medicine is None:
            raise ValueError("Medicine not found.")

        query = (
            self.db.query(InventoryCurrent)
            .join(Facility, Facility.facility_id == InventoryCurrent.facility_id)
            .options(
                joinedload(InventoryCurrent.facility).joinedload(Facility.location),
                joinedload(InventoryCurrent.medicine),
                selectinload(InventoryCurrent.batches),
            )
            .filter(
                InventoryCurrent.medicine_id == medicine_id,
                InventoryCurrent.facility_id != requester_facility_id,
                Facility.is_active.is_(True),
            )
        )
        if not emergency_override:
            query = query.filter(Facility.network_visibility_enabled.is_(True))

        offers = []
        for inventory in query.all():
            quantity, traceable, cold_chain_eligible = self.safe_transferable_quantity(
                inventory,
                datetime.now(timezone.utc).date(),
            )
            if quantity <= 0 or not cold_chain_eligible:
                continue

            distance = self.distance_km(requester.location, inventory.facility.location)
            if distance > radius_km:
                continue

            fulfillment_score = min(quantity / required_quantity, 1.0) * 70
            proximity_score = max(0.0, 1 - distance / radius_km) * 30
            score = round(fulfillment_score + proximity_score, 1)
            offers.append({
                "facility_id": inventory.facility.facility_id,
                "facility_name": inventory.facility.facility_name,
                "facility_type": inventory.facility.facility_type.value,
                "safe_transferable_quantity": quantity,
                "distance_km": round(distance, 2),
                "score": score,
                "batch_traceability_available": traceable,
                "cold_chain_eligible": cold_chain_eligible,
                "recommendation_reason": (
                    f"{quantity} safe units are available {distance:.2f} km away; "
                    "ranked by fulfillment capacity and proximity, not ownership."
                ),
            })

        offers.sort(key=lambda offer: (-offer["score"], offer["distance_km"]))
        if emergency_override:
            AuditService(self.db).record_event(
                action_type="NETWORK_EXCHANGE_EMERGENCY_OVERRIDE",
                entity_type="FACILITY",
                entity_id=requester_facility_id,
                user_id=actor.user_id,
                new_value={
                    "medicine_id": str(medicine_id),
                    "candidate_count": len(offers),
                },
            )
            self.db.flush()
        return offers

    @staticmethod
    def safe_transferable_quantity(
        inventory: InventoryCurrent,
        as_of: date,
    ) -> tuple[int, bool, bool]:
        medicine = inventory.medicine
        facility = inventory.facility
        cold_chain_verified = (
            not medicine.cold_chain_required or facility.cold_chain_capable
        )
        if not cold_chain_verified:
            return 0, bool(inventory.batches), False

        stock_quantity = max(
            int(inventory.available_stock or 0)
            - int(inventory.minimum_threshold or 0),
            0,
        )
        batches = inventory.batches
        if not batches:
            if medicine.cold_chain_required:
                return 0, False, False
            return stock_quantity, False, True

        eligible_batch_quantity = sum(
            max(int(batch.quantity_available or 0), 0)
            for batch in batches
            if batch.status == BatchStatusEnum.AVAILABLE
            and batch.expiry_date is not None
            and batch.expiry_date >= as_of
        )
        return min(stock_quantity, eligible_batch_quantity), True, True

    @staticmethod
    def distance_km(origin, destination) -> float:
        latitude_delta = radians(float(destination.latitude) - float(origin.latitude))
        longitude_delta = radians(float(destination.longitude) - float(origin.longitude))
        origin_latitude = radians(float(origin.latitude))
        destination_latitude = radians(float(destination.latitude))
        haversine = (
            sin(latitude_delta / 2) ** 2
            + cos(origin_latitude)
            * cos(destination_latitude)
            * sin(longitude_delta / 2) ** 2
        )
        return 6371 * 2 * asin(sqrt(haversine))

    def _require_facility_access(self, facility_id: UUID, actor: User) -> None:
        if UserRoleEnum(actor.role) == UserRoleEnum.SYSTEM_ADMIN:
            return
        membership = self.db.query(FacilityUser).filter(
            FacilityUser.facility_id == facility_id,
            FacilityUser.user_id == actor.user_id,
        ).first()
        if membership is None:
            raise PermissionError("User is not authorized for this facility.")