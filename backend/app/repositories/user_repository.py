from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User

from app.repositories.base_repository import (
    BaseRepository
)


class UserRepository(BaseRepository):

    def __init__(self, db: Session):
        super().__init__(db)

    def get_all_users(self):

        query = select(User)

        return (
            self.db.execute(query)
            .scalars()
            .all()
        )

    def get_user_by_id(
        self,
        user_id
    ):

        query = (
            select(User)
            .where(
                User.user_id == user_id
            )
        )

        return (
            self.db.execute(query)
            .scalar_one_or_none()
        )

    def get_user_by_email(
        self,
        email
    ):

        query = (
            select(User)
            .where(
                User.email == email
            )
        )

        return (
            self.db.execute(query)
            .scalar_one_or_none()
        )