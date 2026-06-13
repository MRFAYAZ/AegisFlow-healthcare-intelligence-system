from sqlalchemy.orm import Session

from app.models.user import User

from app.repositories.base_repository import (
    BaseRepository
)

from app.core.security import (
    verify_password,
    create_access_token
)


class AuthService:

    def __init__(self, db: Session):

        self.db = db

    # =====================================================
    # AUTHENTICATE USER
    # =====================================================

    def authenticate_user(
        self,
        email: str,
        password: str
    ):

        user = (
            self.db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        if not user:
            return None

        if not verify_password(
            password,
            user.password_hash
        ):
            return None

        return user

    # =====================================================
    # LOGIN
    # =====================================================

    def login(
        self,
        email: str,
        password: str
    ):

        user = self.authenticate_user(
            email,
            password
        )

        if not user:
            return None

        access_token = (
            create_access_token(
                data={
                    "sub": str(user.user_id),
                    "role": user.role
                }
            )
        )

        return {

            "access_token":
                access_token,

            "token_type":
                "bearer"
        }