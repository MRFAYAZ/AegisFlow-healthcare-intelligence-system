from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.governance.event_log_service import (
    EventLogService
)

router = APIRouter(
    prefix="/event-logs",
    tags=["Event Logs"]
)


# =====================================================
# GET ALL EVENTS
# =====================================================

@router.get("")
def get_all_events(
    db: Session = Depends(get_db)
):

    service = EventLogService(db)

    return service.get_all_events()