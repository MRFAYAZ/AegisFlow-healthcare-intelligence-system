from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.repositories.medicine_repository import (
    MedicineRepository
)

from app.services.medicine.medicine_service import (
    MedicineService
)

from app.schemas.medicine import (
    MedicineCreate,
    MedicineResponse
)

router = APIRouter(
    prefix="/medicines",
    tags=["Medicines"]
)


# =========================================================
# CREATE
# =========================================================

@router.post(
    "",
    response_model=MedicineResponse
)
def create_medicine(
    payload: MedicineCreate,
    db: Session = Depends(get_db)
):

    service = MedicineService(
        MedicineRepository(db)
    )

    try:

        return (
            service.create_medicine(
                payload
            )
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# =========================================================
# GET ALL
# =========================================================

@router.get(
    "",
    response_model=list[MedicineResponse]
)
def get_all_medicines(
    db: Session = Depends(get_db)
):

    service = MedicineService(
        MedicineRepository(db)
    )

    return (
        service.get_all_medicines()
    )


# =========================================================
# GET BY ID
# =========================================================

@router.get(
    "/{medicine_id}",
    response_model=MedicineResponse
)
def get_medicine(
    medicine_id: UUID,
    db: Session = Depends(get_db)
):

    service = MedicineService(
        MedicineRepository(db)
    )

    try:

        return (
            service.get_medicine(
                medicine_id
            )
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )