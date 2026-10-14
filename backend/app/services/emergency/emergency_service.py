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
        """Expose stored decision fields without manufacturing ETA or donor counts."""
        payload = dict(emergency_row)
        payload.setdefault("cascade_safe", None)
        payload.setdefault("estimated_eta_minutes", None)
        payload.setdefault("ai_reason", payload.get("recommendation_reason"))
        payload.setdefault("alternative_donors", None)
        # A straight-line geographic distance is not a validated road travel ETA.
        payload["estimated_eta_minutes"] = None
        return payload

    def get_matches_for_emergency(
        self,
        emergency_case_id,
        max_distance_km: float | None = None,
        user=None,
    ):
        from app.core.enums import UserRoleEnum
        from app.models.emergency import EmergencyCase
        from app.models.facility_user import FacilityUser
        from sqlalchemy import select

        emergency = self.db.get(EmergencyCase, emergency_case_id)
        if emergency is None:
            raise LookupError("Emergency case not found.")
        if user is None:
            raise PermissionError("Authentication is required to view donor matches.")
        if user.role == UserRoleEnum.HOSPITAL_ADMIN:
            membership = self.db.execute(
                select(FacilityUser.facility_user_id).where(
                    FacilityUser.user_id == user.user_id,
                    FacilityUser.facility_id == emergency.facility_id,
                    FacilityUser.assigned_role == UserRoleEnum.HOSPITAL_ADMIN,
                )
            ).scalar_one_or_none()
            if membership is None:
                raise PermissionError("Hospital administrators may only view matches for their assigned facility.")
        elif user.role not in {UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR}:
            raise PermissionError("This role cannot view network-wide donor matches.")

        quantity_needed = max(
            0,
            int(emergency.required_quantity or 0)
            - int(emergency.available_quantity or 0),
        )
        if quantity_needed <= 0:
            return []
        return self.matching_service.find_emergency_sources(
            medicine_id=emergency.medicine_id,
            requesting_facility_id=emergency.facility_id,
            requested_quantity=quantity_needed,
            max_distance_km=max_distance_km,
        )

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

        quantity_needed = max(
            0,
            int(emergency.required_quantity or 0)
            - int(emergency.available_quantity or 0),
        )
        matches = (
            self.matching_service.find_emergency_sources(
                medicine_id=emergency.medicine_id,
                requesting_facility_id=emergency.facility_id,
                requested_quantity=quantity_needed,
                max_distance_km=emergency.emergency_radius_km,
            )
            if quantity_needed > 0
            else []
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