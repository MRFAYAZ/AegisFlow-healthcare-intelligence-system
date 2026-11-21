from typing import List

from pydantic import BaseModel


class ProfileSummary(BaseModel):
    profile_code: str
    profile_name: str
    module_access: list[str]
    is_default: bool = False
    is_active: bool = True

    class Config:
        from_attributes = True


class ProfileAccessResponse(ProfileSummary):
    pass
