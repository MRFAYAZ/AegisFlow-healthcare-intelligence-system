from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_user
from app.core.enums import UserProfileEnum
from app.core.profile_access import PROFILE_ACCESS, PROFILE_LABELS, get_profile_permissions
from app.models.user import User
from app.schemas.profile import ProfileSummary

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("", response_model=list[ProfileSummary])
def list_profiles():
    profiles = []
    for profile_code, label in PROFILE_LABELS.items():
        profiles.append(
            ProfileSummary(
                profile_code=profile_code.value,
                profile_name=label,
                module_access=PROFILE_ACCESS.get(profile_code, []),
                is_default=(profile_code == UserProfileEnum.HOSPITAL_ADMIN),
                is_active=True,
            )
        )
    return profiles


@router.get("/me", response_model=ProfileSummary)
def get_current_profile(current_user: User = Depends(get_current_user)):
    profile_code = UserProfileEnum(current_user.role)
    return ProfileSummary(
        profile_code=profile_code.value,
        profile_name=PROFILE_LABELS.get(profile_code, profile_code.value),
        module_access=get_profile_permissions(profile_code),
        is_default=True,
        is_active=current_user.is_active,
    )
