from uuid import UUID, uuid4

from datetime import datetime, timezone

from sqlalchemy import select

from app.models.audit_log import AuditLog

from app.repositories.base_repository import (
    BaseRepository
)


class AuditRepository(
    BaseRepository
):

    def get_all_logs(self):

        return (
            self.db.execute(
                select(AuditLog).order_by(AuditLog.created_at.asc())
            )
            .scalars()
            .all()
        )

    def get_user_logs(
        self,
        user_id
    ):

        return (
            self.db.execute(
                select(AuditLog)
                .where(
                    AuditLog.user_id
                    ==
                    user_id
                )
            )
            .scalars()
            .all()
        )

    def record_event(
        self,
        action_type: str,
        entity_type: str,
        entity_id: UUID,
        user_id: UUID | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
    ) -> AuditLog:
        event = AuditLog(
            audit_id=uuid4(),
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value or {},
            new_value=new_value or {},
            ip_address=None,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(event)
        self.db.flush()
        return event

    def get_entity_logs(self, entity_type: str, entity_id: UUID):
        query = (
            select(AuditLog)
            .where(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
            .order_by(AuditLog.created_at.asc())
        )
        return self.db.execute(query).scalars().all()