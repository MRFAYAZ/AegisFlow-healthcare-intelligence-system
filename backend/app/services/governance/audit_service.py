from app.repositories.audit_repository import (
    AuditRepository
)


class AuditService:

    def __init__(
        self,
        db
    ):

        self.repository = (
            AuditRepository(db)
        )

    def get_all_logs(self):

        return (
            self.repository
            .get_all_logs()
        )

    def get_user_logs(
        self,
        user_id
    ):

        return (
            self.repository
            .get_user_logs(
                user_id
            )
        )