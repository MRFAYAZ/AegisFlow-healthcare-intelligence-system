from __future__ import annotations

from typing import Iterable

from app.core.enums import UserProfileEnum, UserRoleEnum

PROFILE_ACCESS: dict[UserProfileEnum, list[str]] = {
    UserProfileEnum.SYSTEM_ADMIN: [
        "dashboard",
        "emergency",
        "inventory",
        "shortage",
        "transfers",
        "dispatcher",
        "analytics",
        "map",
        "shop",
        "procurement",
        "network_exchange",
        "profiles",
    ],
    UserProfileEnum.HOSPITAL_ADMIN: [
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
    ],
    UserProfileEnum.PHARMACIST: [
        "dashboard",
        "inventory",
        "shortage",
        "transfers",
        "shop",
        "network_exchange",
    ],
    UserProfileEnum.SHOP_OWNER: [
        "dashboard",
        "inventory",
        "transfers",
        "shop",
        "network_exchange",
    ],
    UserProfileEnum.EMERGENCY_OPERATOR: [
        "dashboard",
        "emergency",
        "shortage",
        "transfers",
        "dispatcher",
        "analytics",
        "map",
        "procurement",
        "network_exchange",
    ],
    UserProfileEnum.DISPATCHER: [
        "dashboard",
        "transfers",
        "dispatcher",
        "map",
    ],
    UserProfileEnum.SUPPLIER_MANAGER: [
        "dashboard",
        "inventory",
        "shortage",
        "procurement",
        "transfers",
        "analytics",
        "map",
        "network_exchange",
    ],
}

PROFILE_LABELS: dict[UserProfileEnum, str] = {
    UserProfileEnum.SYSTEM_ADMIN: "System administrator",
    UserProfileEnum.HOSPITAL_ADMIN: "Hospital administrator",
    UserProfileEnum.PHARMACIST: "Pharmacist",
    UserProfileEnum.SHOP_OWNER: "Shop owner",
    UserProfileEnum.EMERGENCY_OPERATOR: "Emergency operator",
    UserProfileEnum.DISPATCHER: "Dispatcher",
    UserProfileEnum.SUPPLIER_MANAGER: "Supplier manager",
}

ROLE_TO_PROFILE: dict[UserRoleEnum, UserProfileEnum] = {
    UserRoleEnum.SYSTEM_ADMIN: UserProfileEnum.SYSTEM_ADMIN,
    UserRoleEnum.HOSPITAL_ADMIN: UserProfileEnum.HOSPITAL_ADMIN,
    UserRoleEnum.PHARMACIST: UserProfileEnum.PHARMACIST,
    UserRoleEnum.SHOP_OWNER: UserProfileEnum.SHOP_OWNER,
    UserRoleEnum.EMERGENCY_OPERATOR: UserProfileEnum.EMERGENCY_OPERATOR,
    UserRoleEnum.DISPATCHER: UserProfileEnum.DISPATCHER,
    UserRoleEnum.SUPPLIER: UserProfileEnum.SUPPLIER_MANAGER,
}


def resolve_profile(value: str | UserProfileEnum | UserRoleEnum | None) -> UserProfileEnum | None:
    if value is None:
        return None

    normalized = value.value if isinstance(value, (UserProfileEnum, UserRoleEnum)) else str(value)

    try:
        return UserProfileEnum(normalized)
    except ValueError:
        try:
            role = UserRoleEnum(normalized)
            return ROLE_TO_PROFILE.get(role)
        except ValueError:
            return None


def get_profile_permissions(profile_or_role: str | UserProfileEnum | UserRoleEnum | None) -> list[str]:
    profile = resolve_profile(profile_or_role)
    if profile is None:
        return []
    return list(PROFILE_ACCESS.get(profile, []))


def user_has_profile_access(
    profile_or_role: str | UserProfileEnum | UserRoleEnum | None,
    allowed_profiles: Iterable[str | UserProfileEnum | UserRoleEnum],
) -> bool:
    profile = resolve_profile(profile_or_role)
    if profile is None:
        return False

    allowed = {
        resolve_profile(candidate)
        for candidate in allowed_profiles
    }
    allowed.discard(None)
    return profile in allowed
