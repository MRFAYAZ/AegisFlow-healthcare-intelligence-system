from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr
)


class UserResponse(BaseModel):

    user_id: UUID

    full_name: str

    email: EmailStr

    phone_number: str | None = None

    role: str

    is_active: bool

    class Config:
        from_attributes = True