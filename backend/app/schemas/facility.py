from uuid import UUID
from typing import Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field
)

from app.core.enums import (
    FacilityTypeEnum
)

from app.schemas.common import (
    BaseSchema
)


# =========================================================
# CREATE FACILITY
# =========================================================

class FacilityCreate(BaseModel):

    facility_name: str = Field(
        min_length=3,
        max_length=255
    )

    facility_type: FacilityTypeEnum

    location_id: UUID

    license_number: str

    contact_email: EmailStr

    contact_phone: str

    emergency_contact: str

    is_24x7: bool = False


# =========================================================
# UPDATE FACILITY
# =========================================================

class FacilityUpdate(BaseModel):

    facility_name: Optional[str] = None

    contact_email: Optional[
        EmailStr
    ] = None

    contact_phone: Optional[str] = None

    emergency_contact: Optional[
        str
    ] = None

    is_24x7: Optional[bool] = None

    is_active: Optional[bool] = None


# =========================================================
# FACILITY RESPONSE
# =========================================================

class FacilityResponse(BaseSchema):

    facility_id: UUID

    facility_name: str

    facility_type: FacilityTypeEnum

    location_id: UUID

    license_number: str

    contact_email: EmailStr

    contact_phone: str

    emergency_contact: str

    is_24x7: bool

    is_active: bool