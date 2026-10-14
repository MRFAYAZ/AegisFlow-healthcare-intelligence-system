from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.enums import UserRoleEnum
from app.models.facility import Facility
from app.models.facility_user import FacilityUser
from app.models.inventory import InventoryBatch, InventoryCurrent
from app.models.medicine import Medicine
from app.models.user import User
from app.engines.inventory.forecast_engine import project_stockout


class ForecastService:
    """Build explainable stockout projections using expiry-verified available stock."""

    def __init__(self, db: Session):
        self.db = db

    def get_forecasts(self, user: User) -> list[dict]:
        query = (
            select(InventoryCurrent, Facility, Medicine)
            .join(Facility, InventoryCurrent.facility_id == Facility.facility_id)
            .join(Medicine, InventoryCurrent.medicine_id == Medicine.medicine_id)
            .options(
                joinedload(InventoryCurrent.facility),
                joinedload(InventoryCurrent.medicine),
            )
            .where(Facility.is_active.is_(True))
            .order_by(Facility.facility_name, Medicine.medicine_name)
        )

        if user.role == UserRoleEnum.HOSPITAL_ADMIN:
            assigned_facility_ids = self.db.execute(
                select(FacilityUser.facility_id).where(
                    FacilityUser.user_id == user.user_id,
                    FacilityUser.assigned_role == UserRoleEnum.HOSPITAL_ADMIN,
                )
            ).scalars().all()
            if not assigned_facility_ids:
                raise PermissionError("No hospital facility is assigned to this administrator.")
            query = query.where(InventoryCurrent.facility_id.in_(assigned_facility_ids))
        elif user.role not in {UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR}:
            raise PermissionError("This role cannot access network-wide stockout forecasts.")

        inventory_rows = self.db.execute(query).all()
        inventory_ids = [inventory.inventory_id for inventory, _, _ in inventory_rows]
        batches_by_inventory: dict[object, list[InventoryBatch]] = {}
        if inventory_ids:
            batches = self.db.execute(
                select(InventoryBatch)
                .where(InventoryBatch.inventory_id.in_(inventory_ids))
                .order_by(InventoryBatch.expiry_date.asc(), InventoryBatch.batch_id.asc())
            ).scalars().all()
            for batch in batches:
                batches_by_inventory.setdefault(batch.inventory_id, []).append(batch)

        today = date.today()
        results: list[dict] = []
        for inventory, facility, medicine in inventory_rows:
            daily_rate = float(inventory.daily_consumption_rate or 0)
            lead_time = int(
                inventory.lead_time_days
                if inventory.lead_time_days is not None
                else medicine.standard_lead_time_days or 0
            )
            safety_days = int(medicine.safety_stock_days or 0)
            aggregate_available = int(inventory.available_stock or 0)
            inventory_batches = batches_by_inventory.get(inventory.inventory_id, [])
            eligible_batches = [
                batch for batch in inventory_batches
                if batch.expiry_date is not None
                and batch.expiry_date >= today
                and int(batch.quantity_available or 0) > 0
            ]
            verified_batch_available = sum(
                int(batch.quantity_available or 0) for batch in eligible_batches
            )
            usable_stock = min(aggregate_available, verified_batch_available)
            expired_batch_quantity = sum(
                int(batch.quantity_available or 0)
                for batch in inventory_batches
                if batch.expiry_date is not None
                and batch.expiry_date < today
            )
            batch_traceability = (
                "VERIFIED" if eligible_batches
                else "EXPIRED_ONLY" if expired_batch_quantity > 0
                else "UNVERIFIED"
            )

            projection = project_stockout(
                available_stock=usable_stock,
                reserved_stock=int(inventory.reserved_stock or 0),
                daily_consumption_rate=daily_rate,
                lead_time_days=lead_time,
                safety_stock_days=safety_days,
            )
            if aggregate_available > 0 and usable_stock == 0:
                projection.update({
                    "projected_stockout_days": 0.0,
                    "risk_score": 100.0,
                    "risk_level": "CRITICAL",
                    "recommended_action": "SOURCE_NETWORK",
                    "explanation": (
                        "Aggregate inventory reports available stock, but no unexpired, "
                        "batch-traceable available quantity can be verified. Do not treat "
                        "unverified or expired lots as usable emergency supply."
                    ),
                })
            elif usable_stock < aggregate_available:
                projection["explanation"] = (
                    f"Only {usable_stock} of {aggregate_available} aggregate available units "
                    f"are supported by unexpired batch records. "
                    + projection["explanation"]
                )

            results.append({
                "inventory_id": inventory.inventory_id,
                "facility_id": facility.facility_id,
                "facility_name": facility.facility_name,
                "medicine_id": medicine.medicine_id,
                "medicine_name": medicine.medicine_name,
                "available_stock": aggregate_available,
                "reserved_stock": int(inventory.reserved_stock or 0),
                "batch_verified_usable_stock": usable_stock,
                "expired_batch_quantity": expired_batch_quantity,
                "batch_traceability": batch_traceability,
                "eligible_batch_count": len(eligible_batches),
                "daily_consumption_rate": daily_rate,
                "lead_time_days": lead_time,
                "safety_stock_days": safety_days,
                **projection,
            })

        priority = {"CRITICAL": 0, "HIGH": 1, "WARNING": 2, "INSUFFICIENT_DATA": 3, "SAFE": 4}
        results.sort(
            key=lambda row: (
                priority[row["risk_level"]],
                row["projected_stockout_days"]
                if row["projected_stockout_days"] is not None
                else float("inf"),
            )
        )
        return results
