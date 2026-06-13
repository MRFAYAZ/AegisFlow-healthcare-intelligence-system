from app.repositories.event_log_repository import (
    EventLogRepository
)


class EventLogService:

    def __init__(self, db):

        self.repository = (
            EventLogRepository(db)
        )

    def get_all_events(self):

        return (
            self.repository
            .get_all_events()
        )