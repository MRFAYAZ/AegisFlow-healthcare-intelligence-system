from sqlalchemy.orm import Session

from app.services.emergency.matching_service import (
    MatchingService
)

from app.repositories.emergency_repository import (
    EmergencyRepository
)


class EmergencyService:

    def __init__(self, db: Session):

        self.db = db

        self.emergency_repository = (
            EmergencyRepository(db)
        )

        self.matching_service = (
            MatchingService(db)
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

        return (
            self.emergency_repository
            .get_all_emergencies()
        )


    # =====================================================
    # GET ACTIVE EMERGENCIES
    # =====================================================

    def get_active_emergencies(self):

        return (
            self.emergency_repository
            .get_active_emergencies()
        )


    # =====================================================
    # GET CRITICAL EMERGENCIES
    # =====================================================

    def get_critical_emergencies(self):

        return (
            self.emergency_repository
            .get_critical_emergencies()
        )


    # =====================================================
    # DASHBOARD
    # =====================================================

    def get_dashboard(self):

        return (
            self.emergency_repository
            .get_emergency_dashboard()
        )