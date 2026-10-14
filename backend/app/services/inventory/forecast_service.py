from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.enums import UserRoleEnum
from app.models.facility import Facility
from app.models.facility_user import FacilityUser
from app.models.inventory import InventoryCurrent
from app.models.medicine import Medicine
from app.models.user import User
from app.engines.inventory.forecast_engine import project_stockout


class ForecastService:
    """Build explainable per-facility forecasts from persisted inventory values."""

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

        results: list[dict] = []
        for inventory, facility, medicine in self.db.execute(query).all():
            daily_rate = float(inventory.daily_consumption_rate or 0)
            lead_time = int(
                inventory.lead_time_days
                if inventory.lead_time_days is not None
                else medicine.standard_lead_time_days or 0
            )
            safety_days = int(medicine.safety_stock_days or 0)
            projection = project_stockout(
                available_stock=int(inventory.available_stock or 0),
                reserved_stock=int(inventory.reserved_stock or 0),
                daily_consumption_rate=daily_rate,
                lead_time_days=lead_time,
                safety_stock_days=safety_days,
            )
            results.append({
                "inventory_id": inventory.inventory_id,
                "facility_id": facility.facility_id,
                "facility_name": facility.facility_name,
                "medicine_id": medicine.medicine_id,
                "medicine_name": medicine.medicine_name,
                "available_stock": int(inventory.available_stock or 0),
                "reserved_stock": int(inventory.reserved_stock or 0),
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
