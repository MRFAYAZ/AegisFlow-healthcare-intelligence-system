from jose import jwt, JWTError

from fastapi import (
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    OAuth2PasswordBearer
)

from sqlalchemy.orm import Session

from app.core.config import (
    settings
)

from app.core.database import (
    get_db
)

from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


# =========================================================
# GET CURRENT USER
# =========================================================

def get_current_user(

    token: str = Depends(
        oauth2_scheme
    ),

    db: Session = Depends(get_db)

):

    credentials_exception = (
        HTTPException(
            status_code=
            status.HTTP_401_UNAUTHORIZED,

            detail=
            "Could not validate credentials"
        )
    )

    try:

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[
                settings.JWT_ALGORITHM
            ]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = (
        db.query(User)
        .filter(
            User.user_id == user_id
        )
        .first()
    )

    if user is None:
        raise credentials_exception

    return user

from app.core.enums import (
    UserRoleEnum
)


# =========================================================
# ROLE CHECKER
# =========================================================

def require_roles(
    allowed_roles: list[UserRoleEnum]
):

    def role_checker(
        current_user: User = Depends(
            get_current_user
        )
    ):

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        return current_user

    return role_checker