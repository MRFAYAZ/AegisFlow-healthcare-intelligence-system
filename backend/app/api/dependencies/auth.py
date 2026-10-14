from uuid import UUID

from jose import (
    jwt,
    JWTError,
)

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from sqlalchemy.orm import Session

from app.core.config import settings

from app.core.database import get_db

from app.core.enums import (
    UserRoleEnum,
)

from app.models.user import User


# =========================================================
# BEARER TOKEN SCHEME
# =========================================================

bearer_scheme = HTTPBearer()


# =========================================================
# GET CURRENT USER
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:

    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[
                settings.JWT_ALGORITHM,
            ],
        )

        user_id = payload.get("sub")

        if user_id is None:

            raise credentials_exception

        try:

            user_uuid = UUID(
                str(user_id)
            )

        except (
            ValueError,
            TypeError,
        ):

            raise credentials_exception

    except JWTError:

        raise credentials_exception

    user = (
        db.query(User)
        .filter(
            User.user_id == user_uuid
        )
        .first()
    )

    if user is None:

        raise credentials_exception

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


# =========================================================
# ROLE AUTHORIZATION
# =========================================================

def require_roles(
    allowed_roles: list[UserRoleEnum],
):

    def role_checker(
        current_user: User = Depends(
            get_current_user
        ),
    ) -> User:

        try:

            current_role = UserRoleEnum(
                current_user.role
            )

        except ValueError:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "User has an invalid "
                    "application role"
                ),
            )

        if current_role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return current_user

    return role_checker