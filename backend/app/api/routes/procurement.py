from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.procurement import (
    ReplenishmentRequirementResponse, SupplierRecommendationResponse,
    SupplyRequestCreate, SupplyRequestDecision, SupplyRequestResponse,
)
from app.services.procurement_service import ProcurementService

router = APIRouter(prefix="/procurement", tags=["Procurement Intelligence"])


@router.get("/replenishment", response_model=list[ReplenishmentRequirementResponse])
def get_replenishment_requirements(db: Session = Depends(get_db)):
    return ProcurementService(db).get_replenishment_requirements()


@router.get("/suppliers/{medicine_id}", response_model=list[SupplierRecommendationResponse])
def get_supplier_recommendations(medicine_id: UUID, target_facility_id: UUID, requested_quantity: int = Query(gt=0), db: Session = Depends(get_db)):
    return ProcurementService(db).get_supplier_recommendations(medicine_id, target_facility_id, requested_quantity)


@router.post("/supply-requests", response_model=SupplyRequestResponse)
def create_supply_request(payload: SupplyRequestCreate, db: Session = Depends(get_db)):
    try:
        request = ProcurementService(db).create_supply_request(payload)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {
        **request.__dict__,
        "supplier_name": request.supplier.facility_name,
        "target_facility_name": request.target.facility_name,
        "medicine_name": request.medicine.medicine_name,
    }


@router.get("/supply-requests", response_model=list[SupplyRequestResponse])
def get_supply_requests(db: Session = Depends(get_db)):
    return [
        {**request.__dict__, "supplier_name": request.supplier.facility_name, "target_facility_name": request.target.facility_name, "medicine_name": request.medicine.medicine_name}
        for request in ProcurementService(db).get_supply_requests()
    ]


@router.post("/supply-requests/{request_id}/decision", response_model=SupplyRequestResponse)
def decide_supply_request(request_id: UUID, payload: SupplyRequestDecision, db: Session = Depends(get_db)):
    try:
        request = ProcurementService(db).decide_supply_request(request_id, payload.accepted_quantity, payload.response_note)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {
        **request.__dict__,
        "supplier_name": request.supplier.facility_name,
        "target_facility_name": request.target.facility_name,
        "medicine_name": request.medicine.medicine_name,
    }