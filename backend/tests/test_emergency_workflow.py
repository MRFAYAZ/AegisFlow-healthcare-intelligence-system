from uuid import uuid4

from app.core.enums import EmergencyStatusEnum, SeverityEnum, TransferStatusEnum
from app.schemas.emergency import EmergencyResponse


def test_emergency_response_supports_ai_workflow_fields():
    emergency_id = uuid4()
    facility_id = uuid4()
    medicine_id = uuid4()

    response = EmergencyResponse(
        emergency_case_id=emergency_id,
        facility_id=facility_id,
        facility_name="Apollo Hospital",
        medicine_id=medicine_id,
        medicine_name="Salbutamol",
        shortage_score=0.92,
        severity=SeverityEnum.EMERGENCY,
        emergency_radius_km=8,
        required_quantity=120,
        available_quantity=400,
        emergency_status=EmergencyStatusEnum.MATCHING,
        triggered_at="2026-07-05T11:35:00Z",
        resolved_at=None,
        donor_facility="Apollo Hospital",
        transfer_status=TransferStatusEnum.PENDING,
        approved_quantity=120,
        match_score=96.2,
        transfer_distance_km=8.5,
        cascade_safe=True,
        estimated_eta_minutes=18,
        ai_reason="Highest inventory with minimum delivery distance.",
        alternative_donors=4,
    )

    assert response.cascade_safe is True
    assert response.estimated_eta_minutes == 18
    assert response.ai_reason == "Highest inventory with minimum delivery distance."
    assert response.alternative_donors == 4
