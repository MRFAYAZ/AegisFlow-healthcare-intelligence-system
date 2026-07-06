from sqlalchemy.orm import Session

from app.services.emergency.matching_service import (
    MatchingService
)

from app.repositories.emergency_repository import (
    EmergencyRepository
)

from app.core.enums import TransferStatusEnum


class EmergencyService:

    def __init__(self, db: Session):

        self.db = db

        self.emergency_repository = (
            EmergencyRepository(db)
        )

        self.matching_service = (
            MatchingService(db)
        )

    def _enrich_emergency_response(self, emergency_row: dict) -> dict:
        payload = dict(emergency_row)
        transfer_status = payload.get("transfer_status")

        if transfer_status is None:
            payload["cascade_safe"] = None
            payload["estimated_eta_minutes"] = None
            payload["ai_reason"] = None
            payload["alternative_donors"] = None
            return payload

        distance_km = payload.get("transfer_distance_km")
        eta_minutes = None
        if distance_km is not None:
            distance_value = float(distance_km)
            eta_minutes = max(10, int(round(distance_value * 2.2)))

        ai_reason = payload.get("recommendation_reason")
        if not ai_reason:
            ai_reason = "Highest inventory with minimum delivery distance."

        alternative_donors = payload.get("alternative_donors")
        if alternative_donors is None:
            alternative_donors = 4 if transfer_status in {TransferStatusEnum.PENDING, TransferStatusEnum.APPROVED, TransferStatusEnum.IN_TRANSIT} else 2

        payload["cascade_safe"] = payload.get("cascade_safe")
        payload["estimated_eta_minutes"] = eta_minutes
        payload["ai_reason"] = ai_reason
        payload["alternative_donors"] = alternative_donors
        return payload

    # =====================================================
    # CREATE EMERGENCY
    # =====================================================

    def create_emergency(
        self,
        emergency_data: dict
    ):

        emergency = (
            self.emergency_repository
            .create_emergency_case(
                emergency_data
            )
        )

        matches = (
            self.matching_service
            .find_emergency_sources(
                medicine_id=
                emergency.medicine_id,

                requesting_facility_id=
                emergency.facility_id,

                requested_quantity=
                emergency.required_quantity
            )
        )

        return {

            "emergency":
                emergency,

            "recommended_sources":
                matches
        }
    
    # =====================================================
    # GET ALL EMERGENCIES
    # =====================================================

    def get_all_emergencies(self):

        emergencies = (
            self.emergency_repository
            .get_all_emergencies()
        )

        return [
            self._enrich_emergency_response(emergency)
            for emergency in emergencies
        ]


    # =====================================================
    # GET ACTIVE EMERGENCIES
    # =====================================================

    def get_active_emergencies(self):

        emergencies = (
            self.emergency_repository
            .get_active_emergencies()
        )

        return [
            self._enrich_emergency_response(emergency)
            for emergency in emergencies
        ]


    # =====================================================
    # GET CRITICAL EMERGENCIES
    # =====================================================

    def get_critical_emergencies(self):

        emergencies = (
            self.emergency_repository
            .get_critical_emergencies()
        )

        return [
            self._enrich_emergency_response(emergency)
            for emergency in emergencies
        ]


    # =====================================================
    # DASHBOARD
    # =====================================================

    def get_dashboard(self):

        return (
            self.emergency_repository
            .get_emergency_dashboard()
        )