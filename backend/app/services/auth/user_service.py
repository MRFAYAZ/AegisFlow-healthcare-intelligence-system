from app.repositories.user_repository import (
    UserRepository
)


class UserService:

    def __init__(self, db):

        self.repository = (
            UserRepository(db)
        )

    def get_all_users(self):

        return (
            self.repository
            .get_all_users()
        )

    def get_user_by_id(
        self,
        user_id
    ):

        return (
            self.repository
            .get_user_by_id(
                user_id
            )
        )