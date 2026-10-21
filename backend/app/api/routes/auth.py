from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.models.facility_user import FacilityUser
from sqlalchemy import select

from app.services.auth.auth_service import (
    AuthService
)

from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    CurrentUserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =====================================================
# LOGIN
# =====================================================

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):

    service = AuthService(db)

    result = service.login(
        email=payload.email,
        password=payload.password
    )

    if not result:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return result

@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Return the authenticated user's identity and role",
)
def get_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    facility_ids = db.execute(
        select(FacilityUser.facility_id).where(
            FacilityUser.user_id == current_user.user_id
        )
    ).scalars().all()
    return {
        "user_id": str(current_user.user_id),
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
        "facility_ids": facility_ids,
    }
