from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.emergency import (
    EmergencyCase,
    EmergencySourceMatch
)

from app.core.enums import (
    EmergencyStatusEnum,
    SeverityEnum
)

from app.repositories.base_repository import (
    BaseRepository
)


class EmergencyRepository(BaseRepository):

    def __init__(self, db: Session):
        super().__init__(db)

    # =====================================================
    # GET ACTIVE EMERGENCIES
    # =====================================================

    def get_active_emergencies(self):

        query = (
            select(EmergencyCase)
            .where(
                EmergencyCase.emergency_status.in_([
                    EmergencyStatusEnum.ACTIVE,
                    EmergencyStatusEnum.MATCHING
                ])
            )
        )

        return self.db.execute(query).scalars().all()

    # =====================================================
    # GET CRITICAL EMERGENCIES
    # =====================================================

    def get_critical_emergencies(self):

        query = (
            select(EmergencyCase)
            .where(
                EmergencyCase.severity.in_([
                    SeverityEnum.CRITICAL,
                    SeverityEnum.EMERGENCY
                ])
            )
        )

        return self.db.execute(query).scalars().all()

    # =====================================================
    # GET MATCHES FOR EMERGENCY
    # =====================================================

    def get_matches_for_emergency(
        self,
        emergency_case_id
    ):

        query = (
            select(EmergencySourceMatch)
            .where(
                EmergencySourceMatch
                .emergency_case_id
                == emergency_case_id
            )
        )

        return self.db.execute(query).scalars().all()

    # =====================================================
    # CREATE EMERGENCY CASE
    # =====================================================

    def create_emergency_case(
        self,
        emergency_data
    ):

        emergency = EmergencyCase(
            **emergency_data
        )

        self.db.add(emergency)

        self.db.commit()

        self.db.refresh(emergency)

        return emergency
    
    # =====================================================
    # GET ALL EMERGENCIES
    # =====================================================

    def get_all_emergencies(self):

        query = select(EmergencyCase)

        return (
            self.db.execute(query)
            .scalars()
            .all()
        )
    
    # =====================================================
    # EMERGENCY DASHBOARD
    # =====================================================

    def get_emergency_dashboard(self):

        emergencies = (
            self.get_all_emergencies()
        )

        return {
            
            "total_emergencies":
            len(emergencies),

            "active":
                len(
                    [
                        e for e in emergencies
                        if e.emergency_status
                        ==
                        EmergencyStatusEnum.ACTIVE
                    ]
                ),

            "matching":
                len(
                    [
                        e for e in emergencies
                        if e.emergency_status
                        ==
                        EmergencyStatusEnum.MATCHING
                    ]
                ),

            "resolved":
                len(
                    [
                        e for e in emergencies
                        if e.emergency_status
                        ==
                        EmergencyStatusEnum.RESOLVED
                    ]
                ),

            "critical":
                len(
                    [
                        e for e in emergencies
                        if e.severity
                        ==
                        SeverityEnum.CRITICAL
                    ]
                ),

            "emergency":
                len(
                    [
                        e for e in emergencies
                        if e.severity
                        ==
                        SeverityEnum.EMERGENCY
                    ]
                )
        }
            