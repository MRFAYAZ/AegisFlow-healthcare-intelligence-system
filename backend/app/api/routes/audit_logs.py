from uuid import UUID

from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.governance.audit_service import (
    AuditService
)

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


@router.get("")
def get_logs(
    db: Session = Depends(get_db)
):

    return (
        AuditService(db)
        .get_all_logs()
    )


@router.get("/user/{user_id}")
def get_user_logs(
    user_id: UUID,
    db: Session = Depends(get_db)
):

    return (
        AuditService(db)
        .get_user_logs(
            user_id
        )
    )