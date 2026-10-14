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

    def record_event(
        self,
        action_type,
        entity_type,
        entity_id,
        user_id=None,
        old_value=None,
        new_value=None,
    ):
        return self.repository.record_event(
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            old_value=old_value,
            new_value=new_value,
        )

    def get_entity_logs(self, entity_type, entity_id):
        return self.repository.get_entity_logs(entity_type, entity_id)