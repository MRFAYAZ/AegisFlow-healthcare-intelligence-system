from app.core.enums import UserRoleEnum
from app.core.profile_access import get_profile_permissions, user_has_profile_access


def test_profile_access_matches_role_permissions():
    assert get_profile_permissions(UserRoleEnum.HOSPITAL_ADMIN) == [
        "dashboard",
        "emergency",
        "inventory",
        "shortage",
        "transfers",
        "procurement",
        "analytics",
        "map",
        "network_exchange",
        "profiles",
    ]


def test_profile_gate_allows_only_configured_profiles():
    assert user_has_profile_access(UserRoleEnum.EMERGENCY_OPERATOR, ["EMERGENCY_OPERATOR", "SYSTEM_ADMIN"])
    assert not user_has_profile_access(UserRoleEnum.HOSPITAL_ADMIN, ["DISPATCHER", "SYSTEM_ADMIN"])
