from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import UserRoleEnum
from app.api.dependencies.auth import require_roles

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


@router.get("/emergency/{emergency_id}")
def get_emergency_timeline(
    emergency_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles([
            UserRoleEnum.SYSTEM_ADMIN,
            UserRoleEnum.HOSPITAL_ADMIN,
            UserRoleEnum.EMERGENCY_OPERATOR,
            UserRoleEnum.DISPATCHER,
        ])
    ),
):
    logs = AuditService(db).get_entity_logs(
        entity_type="EMERGENCY",
        entity_id=emergency_id,
    )
    return [
        {
            "audit_id": str(log.audit_id),
            "action_type": log.action_type,
            "entity_type": log.entity_type,
            "entity_id": str(log.entity_id),
            "old_value": log.old_value,
            "new_value": log.new_value,
            "created_at": log.created_at,
        }
        for log in logs
    ]