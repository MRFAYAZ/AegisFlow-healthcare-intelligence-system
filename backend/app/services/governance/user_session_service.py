from app.repositories.user_session_repository import (
    UserSessionRepository
)


class UserSessionService:

    def __init__(self, db):

        self.repository = (
            UserSessionRepository(db)
        )

    def get_all_sessions(self):

        return (
            self.repository
            .get_all_sessions()
        )

    def get_active_sessions(self):

        return (
            self.repository
            .get_active_sessions()
        )