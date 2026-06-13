from sqlalchemy import select

from app.models.event_log import EventLog

from app.repositories.base_repository import (
    BaseRepository
)


class EventLogRepository(
    BaseRepository
):

    def get_all_events(self):

        return (
            self.db.execute(
                select(EventLog)
            )
            .scalars()
            .all()
        )