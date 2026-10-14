from datetime import datetime, timedelta, timezone
from math import asin, cos, radians, sin, sqrt
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.enums import FacilityTypeEnum, SupplyRequestStatusEnum
from app.models.facility import Facility
from app.models.inventory import InventoryCurrent
from app.models.procurement import ReplenishmentRequirement, SupplyRequest
from app.services.inventory.inventory_service import InventoryService


def _distance_km(source: Facility, target: Facility) -> float | None:
    if not source.location or not target.location:
        return None
    lat1, lon1 = float(source.location.latitude), float(source.location.longitude)
    lat2, lon2 = float(target.location.latitude), float(target.location.longitude)
    delta_lat, delta_lon = radians(lat2 - lat1), radians(lon2 - lon1)
    value = sin(delta_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(delta_lon / 2) ** 2
    return round(6371 * 2 * asin(sqrt(value)), 1)


class ProcurementService:
    def __init__(self, db):
        self.db = db
        self.inventory_service = InventoryService(db)

    def get_replenishment_requirements(self):
        requirements = []
        for risk in self.inventory_service.get_shortage_risk_assessments():
            if risk["risk_level"] == "SAFE":
                continue
            daily = risk["daily_consumption"]
            target_stock = risk["safety_stock_units"] + daily * risk["lead_time_days"]
            requested_quantity = max(1, round(target_stock - risk["usable_stock"]))
            requirements.append({
                "requirement_id": None,
                "inventory_id": risk["inventory_id"],
                "facility_id": risk["facility_id"],
                "medicine_id": risk["medicine_id"],
                "facility_name": risk["facility_name"],
                "medicine_name": risk["medicine_name"],
                "requested_quantity": requested_quantity,
                "priority": risk["risk_level"],
                "projected_stockout_days": risk["projected_stockout_days"],
                "required_by_days": risk["lead_time_days"],
                "reason": "Projected stockout before the normal replenishment cycle.",
                "status": "OPEN",
            })
        return requirements

    def get_supplier_recommendations(self, medicine_id: UUID, target_facility_id: UUID, requested_quantity: int):
        target = self.db.execute(
            select(Facility).options(joinedload(Facility.location)).where(Facility.facility_id == target_facility_id)
        ).scalar_one()
        rows = self.db.execute(
            select(InventoryCurrent)
            .options(joinedload(InventoryCurrent.facility).joinedload(Facility.location), joinedload(InventoryCurrent.medicine))
            .join(InventoryCurrent.facility)
            .where(InventoryCurrent.medicine_id == medicine_id, Facility.facility_type == FacilityTypeEnum.SUPPLIER)
        ).scalars().all()
        recommendations = []
        for row in rows:
            available = max(int(row.total_stock or 0) - int(row.reserved_stock or 0), 0)
            lead_time = max(int(row.lead_time_days or 0), 0)
            distance = _distance_km(row.facility, target)
            availability_score = min(45.0, available / max(requested_quantity, 1) * 45)
            lead_score = max(0.0, 30.0 - lead_time * 5)
            distance_score = max(0.0, 25.0 - (distance or 0) / 10)
            score = round(min(100.0, availability_score + lead_score + distance_score), 1)
            recommendations.append({
                "supplier_facility_id": row.facility_id,
                "supplier_name": row.facility.facility_name,
                "medicine_id": row.medicine_id,
                "medicine_name": row.medicine.medicine_name,
                "available_quantity": available,
                "requested_quantity": requested_quantity,
                "lead_time_days": lead_time,
                "distance_km": distance,
                "readiness_score": score,
                "reliability_status": "Not yet measured",
                "recommendation_reason": "Ranked by usable availability, lead time, distance, and medicine match.",
            })
        return sorted(recommendations, key=lambda item: item["readiness_score"], reverse=True)

    def create_supply_request(self, data):
        risk = next((item for item in self.inventory_service.get_shortage_risk_assessments() if item["inventory_id"] == data.inventory_id), None)
        if not risk:
            raise ValueError("Inventory risk assessment not found")
        requirement = ReplenishmentRequirement(
            facility_id=risk["facility_id"], medicine_id=risk["medicine_id"], requested_quantity=data.requested_quantity,
            priority=risk["risk_level"] if risk["risk_level"] != "HIGH" else "CRITICAL",
            required_by=datetime.now(timezone.utc) + timedelta(days=risk["lead_time_days"]),
            reason="Created from predictive shortage intelligence.", status="PENDING_APPROVAL",
        )
        self.db.add(requirement)
        self.db.flush()
        supplier = next((item for item in self.get_supplier_recommendations(risk["medicine_id"], risk["facility_id"], data.requested_quantity) if item["supplier_facility_id"] == data.supplier_facility_id), None)
        if not supplier:
            raise ValueError("Supplier recommendation not found")
        request = SupplyRequest(
            requirement_id=requirement.requirement_id, supplier_facility_id=data.supplier_facility_id,
            target_facility_id=risk["facility_id"], medicine_id=risk["medicine_id"], requested_quantity=data.requested_quantity,
            lead_time_days=supplier["lead_time_days"], recommendation_score=supplier["readiness_score"],
            status=SupplyRequestStatusEnum.PENDING_APPROVAL,
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def get_supply_requests(self):
        return self.db.execute(
            select(SupplyRequest)
            .options(joinedload(SupplyRequest.supplier), joinedload(SupplyRequest.target), joinedload(SupplyRequest.medicine))
            .order_by(SupplyRequest.created_at.desc())
        ).scalars().all()

    def decide_supply_request(self, request_id: UUID, accepted_quantity: int, response_note: str | None = None):
        request = self.db.get(SupplyRequest, request_id)
        if not request:
            raise ValueError("Supply request not found")
        if accepted_quantity > request.requested_quantity:
            raise ValueError("Accepted quantity cannot exceed requested quantity")
        request.accepted_quantity = accepted_quantity
        request.response_note = response_note
        request.responded_at = datetime.now(timezone.utc)
        request.status = (
            SupplyRequestStatusEnum.ACCEPTED if accepted_quantity == request.requested_quantity
            else SupplyRequestStatusEnum.PARTIALLY_FULFILLED if accepted_quantity > 0
            else SupplyRequestStatusEnum.DECLINED
        )
        self.db.commit()
        self.db.refresh(request)
        return request