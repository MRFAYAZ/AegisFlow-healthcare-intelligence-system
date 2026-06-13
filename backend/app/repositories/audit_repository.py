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
                select(AuditLog)
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