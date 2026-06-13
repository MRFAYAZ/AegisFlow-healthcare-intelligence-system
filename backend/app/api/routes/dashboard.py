from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.analytics.dashboard_service import (
    DashboardService
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/snapshot")
def get_dashboard_snapshot(
    db: Session = Depends(get_db)
):

    return (
        DashboardService(db)
        .get_dashboard_snapshot()
    )


@router.get("/review")
def get_review_dashboard(
    db: Session = Depends(get_db)
):

    return (
        DashboardService(db)
        .get_review_dashboard()
    )