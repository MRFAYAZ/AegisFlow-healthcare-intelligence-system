from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.auth.user_service import (
    UserService
)

from app.schemas.user import (
    UserResponse
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "",
    response_model=list[UserResponse]
)
def get_all_users(
    db: Session = Depends(get_db)
):

    service = UserService(db)

    return service.get_all_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):

    service = UserService(db)

    user = (
        service.get_user_by_id(
            user_id
        )
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user