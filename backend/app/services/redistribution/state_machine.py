"""Allowed lifecycle transitions for AegisFlow transfer requests."""

from app.core.enums import TransferStatusEnum


_ALLOWED_TRANSITIONS: dict[TransferStatusEnum, set[TransferStatusEnum]] = {
    TransferStatusEnum.PENDING: {
        TransferStatusEnum.APPROVED,
        TransferStatusEnum.REJECTED,
        TransferStatusEnum.CANCELLED,
    },
    TransferStatusEnum.APPROVED: {
        TransferStatusEnum.IN_TRANSIT,
        TransferStatusEnum.CANCELLED,
    },
    TransferStatusEnum.IN_TRANSIT: {
        TransferStatusEnum.COMPLETED,
        TransferStatusEnum.CANCELLED,
    },
    TransferStatusEnum.REJECTED: set(),
    TransferStatusEnum.COMPLETED: set(),
    TransferStatusEnum.CANCELLED: set(),
}


def validate_transfer_transition(
    current: TransferStatusEnum,
    target: TransferStatusEnum,
) -> None:
    """Raise ValueError unless target is an allowed next transfer status."""
    if target not in _ALLOWED_TRANSITIONS.get(current, set()):
        raise ValueError(
            f"Invalid transfer transition: {current.value} -> {target.value}."
        )
