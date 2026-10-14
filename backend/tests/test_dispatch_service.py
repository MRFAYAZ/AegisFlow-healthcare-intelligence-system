from app.core.enums import EmergencyStatusEnum, TransferStatusEnum
from app.models.dispatch import DispatchStatusEnum
from app.repositories.emergency_repository import EmergencyRepository
from app.services.emergency.emergency_service import EmergencyService


def test_dispatch_status_values_are_defined():
    assert DispatchStatusEnum.ASSIGNED.value == "ASSIGNED"
    assert DispatchStatusEnum.IN_TRANSIT.value == "IN_TRANSIT"
    assert DispatchStatusEnum.DELIVERED.value == "DELIVERED"

    assert TransferStatusEnum.APPROVED.value == "APPROVED"
    assert TransferStatusEnum.IN_TRANSIT.value == "IN_TRANSIT"
    assert TransferStatusEnum.COMPLETED.value == "COMPLETED"


def test_emergency_fulfillment_tracking_is_supported():
    assert EmergencyStatusEnum.PARTIALLY_RESOLVED.value == "PARTIALLY_RESOLVED"
    assert EmergencyStatusEnum.RESOLVED.value == "RESOLVED"

    emergency_service = EmergencyService(None)
    emergency_repository = EmergencyRepository(None)

    assert hasattr(emergency_service, "update_emergency_fulfillment")
    assert hasattr(emergency_repository, "get_completed_transfer_quantity")
