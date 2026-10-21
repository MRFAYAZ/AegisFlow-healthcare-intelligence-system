from sqlalchemy.orm import (
    Session,
    aliased
)
from sqlalchemy import select

from app.models.facility import Facility
from app.models.location import Location
from app.models.medicine import Medicine
from app.models.redistribution import TransferRequest
from app.models.dispatch import TransferDispatch

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
    # BASE EMERGENCY QUERY
    # =====================================================

    def _base_emergency_query(self):

        DonorFacility = aliased(Facility)
        FacilityLocation = aliased(Location)
        DonorLocation = aliased(Location)

        return (
            select(

                EmergencyCase.emergency_case_id,

                EmergencyCase.facility_id,
                Facility.facility_name.label("facility_name"),
                FacilityLocation.latitude.label("facility_latitude"),
                FacilityLocation.longitude.label("facility_longitude"),

                EmergencyCase.medicine_id,
                Medicine.medicine_name.label("medicine_name"),

                EmergencyCase.shortage_score,
                EmergencyCase.severity,
                EmergencyCase.emergency_radius_km,

                EmergencyCase.required_quantity,
                EmergencyCase.available_quantity,

                EmergencyCase.emergency_status,

                EmergencyCase.triggered_at,
                EmergencyCase.resolved_at,

                TransferRequest.transfer_id,

                TransferRequest.transfer_status,

                TransferRequest.approved_quantity,

                TransferRequest.match_score,

                TransferRequest.transfer_distance_km,

                TransferRequest.cascade_safe,

                TransferRequest.recommendation_reason,
                TransferRequest.requested_at,
                TransferRequest.approved_at,
                TransferRequest.completed_at,
                TransferRequest.rejection_reason,
                TransferDispatch.status.label("dispatch_status"),
                TransferDispatch.transport_type,
                TransferDispatch.vehicle_reference,
                TransferDispatch.dispatched_at,
                TransferDispatch.delivered_at,

                DonorFacility.facility_name.label("donor_facility"),
                DonorLocation.latitude.label("donor_latitude"),
                DonorLocation.longitude.label("donor_longitude")

            )

            .join(
                Facility,
                EmergencyCase.facility_id ==
                Facility.facility_id
            )

            .join(
                FacilityLocation,
                Facility.location_id == FacilityLocation.location_id
            )
            .join(
                Medicine,
                EmergencyCase.medicine_id ==
                Medicine.medicine_id
            )

            .outerjoin(
                TransferRequest,
                EmergencyCase.emergency_case_id ==
                TransferRequest.emergency_case_id
            )

            .outerjoin(
                TransferDispatch,
                TransferRequest.transfer_id == TransferDispatch.transfer_id
            )
            .outerjoin(
                DonorFacility,
                TransferRequest.from_facility_id ==
                DonorFacility.facility_id
            )
            .outerjoin(
                DonorLocation,
                DonorFacility.location_id == DonorLocation.location_id
            )
            # Emergency cards show one latest transfer summary per emergency.
            # The transfer-list API remains the source for viewing every leg.
            .distinct(EmergencyCase.emergency_case_id)
            .order_by(
                EmergencyCase.emergency_case_id,
                TransferRequest.requested_at.desc().nullslast(),
            )
        )
    # =====================================================
    # GET ACTIVE EMERGENCIES
    # =====================================================

    def get_active_emergencies(self):


        query = (
            self._base_emergency_query()

            .where(
                EmergencyCase.emergency_status.in_(
                    [
                        EmergencyStatusEnum.ACTIVE,
                        EmergencyStatusEnum.MATCHING
                    ]
                )
            )
        )
        return self.db.execute(query).mappings().all()

    # =====================================================
    # GET CRITICAL EMERGENCIES
    # =====================================================

    def get_critical_emergencies(self):

        query = (
            self._base_emergency_query()

            .where(
                EmergencyCase.severity.in_(
                    [
                        SeverityEnum.CRITICAL,
                        SeverityEnum.EMERGENCY
                    ]
                )
            )
        )
        return self.db.execute(query).mappings().all()

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

        query = self._base_emergency_query()

        return (
            self.db.execute(query)
            .mappings()
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
                        if e["emergency_status"]
                        ==
                        EmergencyStatusEnum.ACTIVE
                    ]
                ),

            "matching":
                len(
                    [
                        e for e in emergencies
                        if e["emergency_status"]
                        ==
                        EmergencyStatusEnum.MATCHING
                    ]
                ),

            "resolved":
                len(
                    [
                        e for e in emergencies
                        if e["emergency_status"]
                        ==
                        EmergencyStatusEnum.RESOLVED
                    ]
                ),

            "critical":
                len(
                    [
                        e for e in emergencies
                        if e["severity"]
                        ==
                        SeverityEnum.CRITICAL
                    ]
                ),

            "emergency":
                len(
                    [
                        e for e in emergencies
                        if e["severity"]
                        ==
                        SeverityEnum.EMERGENCY
                    ]
                )
        }
            