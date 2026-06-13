from datetime import datetime

from sqlalchemy import select

from app.models.user_session import (
    UserSession
)

from app.repositories.base_repository import (
    BaseRepository
)


class UserSessionRepository(
    BaseRepository
):

    def get_all_sessions(self):

        return (
            self.db.execute(
                select(UserSession)
            )
            .scalars()
            .all()
        )

    def get_active_sessions(self):

        return (
            self.db.execute(
                select(UserSession)
                .where(
                    UserSession.expires_at
                    >
                    datetime.utcnow()
                )
            )
            .scalars()
            .all()
        )