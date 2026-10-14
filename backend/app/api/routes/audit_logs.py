from uuid import UUID

from fastapi import (
    APIRouter,
    Depends
)

from app.api.dependencies.auth import require_roles
from app.core.enums import UserRoleEnum
from app.models.user import User

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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.SYSTEM_ADMIN])),
):

    return (
        AuditService(db)
        .get_all_logs()
    )


@router.get("/user/{user_id}")
def get_user_logs(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRoleEnum.SYSTEM_ADMIN])),
):

    return (
        AuditService(db)
        .get_user_logs(
            user_id
        )
    )