from uuid import UUID

from fastapi import (
    APIRouter,
    Depends
)
from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.redistribution.redistribution_service import (
    RedistributionService
)

from app.schemas.redistribution import (
    TransferResponse
)

router = APIRouter(
    prefix="/redistribution",
    tags=["Redistribution"]
)


class DispatchRequest(BaseModel):
    emergency_case_id: UUID

@router.get(
    "",
    response_model=list[TransferResponse]
)
def get_all_transfers(
    db: Session = Depends(get_db)
):
    service = RedistributionService(db)

    return service.get_all_transfers()

@router.get(
    "/high-priority",
    response_model=list[TransferResponse]
)
def get_high_priority(
    db: Session = Depends(get_db)
):
    service = RedistributionService(db)
    return service.get_high_priority_transfers()

@router.get(
    "/facility/{facility_id}",
    response_model=list[TransferResponse]
)
def get_facility_transfers(
    facility_id: UUID,
    db: Session = Depends(get_db)
):
    
    service = RedistributionService(db)

    return service.get_facility_transfers(
        facility_id
    )

@router.get(
    "/dashboard"
)
def get_dashboards(
    db: Session = Depends(get_db)
):
    service = RedistributionService(db)

    return service.get_dashboard()


@router.post(
    "/dispatch"
)
def dispatch_transfer(
    payload: DispatchRequest,
    db: Session = Depends(get_db)
):
    service = RedistributionService(db)

    return service.dispatch_transfer(
        payload.emergency_case_id
    )