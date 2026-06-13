from pydantic import (
    BaseModel,
    EmailStr
)

from app.core.enums import (
    UserRoleEnum
)


# =========================================================
# LOGIN REQUEST
# =========================================================

class LoginRequest(BaseModel):

    email: EmailStr

    password: str


# =========================================================
# TOKEN RESPONSE
# =========================================================

class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"


# =========================================================
# CURRENT USER RESPONSE
# =========================================================

class CurrentUserResponse(BaseModel):

    user_id: str

    full_name: str

    email: EmailStr

    role: UserRoleEnum