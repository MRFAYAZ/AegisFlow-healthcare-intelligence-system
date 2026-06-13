from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class FacilityUserResponse(
    BaseModel
):

    facility_user_id: UUID

    facility_id: UUID

    user_id: UUID

    assigned_role: str

    assigned_at: datetime

    class Config:
        from_attributes = True