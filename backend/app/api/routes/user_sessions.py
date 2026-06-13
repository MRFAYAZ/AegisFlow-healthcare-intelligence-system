from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.governance.user_session_service import (
    UserSessionService
)

router = APIRouter(
    prefix="/user-sessions",
    tags=["User Sessions"]
)


# =====================================================
# GET ALL SESSIONS
# =====================================================

@router.get("")
def get_all_sessions(
    db: Session = Depends(get_db)
):

    service = UserSessionService(db)

    return service.get_all_sessions()


# =====================================================
# GET ACTIVE SESSIONS
# =====================================================

@router.get("/active")
def get_active_sessions(
    db: Session = Depends(get_db)
):

    service = UserSessionService(db)

    return service.get_active_sessions()