import pytest

from app.core.enums import TransferStatusEnum
from app.services.redistribution.state_machine import validate_transfer_transition


@pytest.mark.parametrize(
    "current,target",
    [
        (TransferStatusEnum.PENDING, TransferStatusEnum.APPROVED),
        (TransferStatusEnum.PENDING, TransferStatusEnum.REJECTED),
        (TransferStatusEnum.APPROVED, TransferStatusEnum.IN_TRANSIT),
        (TransferStatusEnum.IN_TRANSIT, TransferStatusEnum.COMPLETED),
    ],
)
def test_valid_transfer_transitions(current, target):
    validate_transfer_transition(current, target)


@pytest.mark.parametrize(
    "current,target",
    [
        (TransferStatusEnum.PENDING, TransferStatusEnum.IN_TRANSIT),
        (TransferStatusEnum.APPROVED, TransferStatusEnum.COMPLETED),
        (TransferStatusEnum.REJECTED, TransferStatusEnum.APPROVED),
        (TransferStatusEnum.COMPLETED, TransferStatusEnum.IN_TRANSIT),
        (TransferStatusEnum.CANCELLED, TransferStatusEnum.APPROVED),
    ],
)
def test_invalid_transfer_transitions_are_rejected(current, target):
    with pytest.raises(ValueError, match="Invalid transfer transition"):
        validate_transfer_transition(current, target)
