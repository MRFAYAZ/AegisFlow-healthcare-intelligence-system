from sqlalchemy.orm import (
    Session,
    aliased
)
from sqlalchemy import func, select

from app.models.facility import Facility
from app.models.medicine import Medicine
from app.models.redistribution import TransferRequest
from app.models.location import Location

from app.models.emergency import (
    EmergencyCase,
    EmergencySourceMatch
)

from app.core.enums import (
    EmergencyStatusEnum,
    SeverityEnum,
    TransferStatusEnum,
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

    def get_completed_transfer_quantity(
        self,
        emergency_case_id,
    ):
        query = (
            select(
                func.coalesce(
                    func.sum(
                        TransferRequest.approved_quantity
                    ),
                    0,
                )
            )
            .where(
                TransferRequest.emergency_case_id == emergency_case_id,
                TransferRequest.transfer_status == TransferStatusEnum.COMPLETED,
            )
        )

        return self.db.execute(query).scalar_one()

    def _base_emergency_query(self):

        DonorFacility = aliased(Facility)

        FacilityLocation = aliased(Location)

        DonorLocation = aliased(Location)

        return (
            select(

                EmergencyCase.emergency_case_id,

                EmergencyCase.facility_id,

                Facility.facility_name.label(
                    "facility_name"
                ),

                # -------------------------------------------------
                # Requesting facility coordinates
                # -------------------------------------------------

                FacilityLocation.latitude.label(
                    "facility_latitude"
                ),

                FacilityLocation.longitude.label(
                    "facility_longitude"
                ),

                # -------------------------------------------------
                # Medicine
                # -------------------------------------------------

                EmergencyCase.medicine_id,

                Medicine.medicine_name.label(
                    "medicine_name"
                ),

                # -------------------------------------------------
                # Emergency information
                # -------------------------------------------------

                EmergencyCase.shortage_score,

                EmergencyCase.severity,

                EmergencyCase.emergency_radius_km,

                EmergencyCase.required_quantity,

                EmergencyCase.available_quantity,

                EmergencyCase.emergency_status,

                EmergencyCase.triggered_at,

                EmergencyCase.resolved_at,

                # -------------------------------------------------
                # Transfer information
                # -------------------------------------------------

                TransferRequest.transfer_id,

                TransferRequest.transfer_status,

                TransferRequest.approved_quantity,

                TransferRequest.match_score,

                TransferRequest.transfer_distance_km,

                TransferRequest.cascade_safe,

                TransferRequest.recommendation_reason,

                # -------------------------------------------------
                # Donor facility
                # -------------------------------------------------

                DonorFacility.facility_name.label(
                    "donor_facility"
                ),

                # -------------------------------------------------
                # Donor coordinates
                # -------------------------------------------------

                DonorLocation.latitude.label(
                    "donor_latitude"
                ),

                DonorLocation.longitude.label(
                    "donor_longitude"
                )

            )

            # =====================================================
            # REQUESTING FACILITY
            # =====================================================

            .join(
                Facility,
                EmergencyCase.facility_id
                == Facility.facility_id
            )

            # =====================================================
            # REQUESTING FACILITY LOCATION
            # =====================================================

            .join(
                FacilityLocation,
                Facility.location_id
                == FacilityLocation.location_id
            )

            # =====================================================
            # MEDICINE
            # =====================================================

            .join(
                Medicine,
                EmergencyCase.medicine_id
                == Medicine.medicine_id
            )

            # =====================================================
            # TRANSFER
            # =====================================================

            .outerjoin(
                TransferRequest,
                EmergencyCase.emergency_case_id
                == TransferRequest.emergency_case_id
            )

            # =====================================================
            # DONOR FACILITY
            # =====================================================

            .outerjoin(
                DonorFacility,
                TransferRequest.from_facility_id
                == DonorFacility.facility_id
            )

            # =====================================================
            # DONOR LOCATION
            # =====================================================

            .outerjoin(
                DonorLocation,
                DonorFacility.location_id
                == DonorLocation.location_id
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

        return (
            self.db.execute(query)
            .mappings()
            .all()
        )

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

        return (
            self.db.execute(query)
            .mappings()
            .all()
        )

    # =====================================================
    # GET MATCHES FOR EMERGENCY
    # =====================================================

    def get_matches_for_emergency(
        self,
        emergency_case_id
    ):

        DonorFacility = aliased(Facility)

        query = (
            select(

                # -------------------------------------------------
                # Match identity
                # -------------------------------------------------

                EmergencySourceMatch.match_id,

                EmergencySourceMatch.emergency_case_id,

                EmergencySourceMatch.source_facility_id,

                # -------------------------------------------------
                # Donor facility
                # -------------------------------------------------

                DonorFacility.facility_name.label(
                    "facility_name"
                ),

                # -------------------------------------------------
                # Medicine
                # -------------------------------------------------

                EmergencySourceMatch.medicine_id,

                # -------------------------------------------------
                # Inventory information
                # -------------------------------------------------

                EmergencySourceMatch.available_quantity,

                EmergencySourceMatch.transferable_quantity,
                EmergencySourceMatch.selected_batch_number,
                EmergencySourceMatch.earliest_expiry_date,
                EmergencySourceMatch.cold_chain_required,
                EmergencySourceMatch.cold_chain_capable,
                EmergencySourceMatch.safety_status,
                EmergencySourceMatch.safety_reason,
                EmergencySourceMatch.batch_allocations,

                EmergencySourceMatch.donor_shortage_score,

                # -------------------------------------------------
                # Geographic information
                # -------------------------------------------------

                EmergencySourceMatch.distance_km,

                EmergencySourceMatch.distance_score,

                # -------------------------------------------------
                # Matching information
                # -------------------------------------------------

                EmergencySourceMatch.inventory_score,

                EmergencySourceMatch.donor_health_score,

                EmergencySourceMatch.ranking_score,

                EmergencySourceMatch.is_selected,

                EmergencySourceMatch.matched_at

            )

            .join(
                DonorFacility,
                EmergencySourceMatch.source_facility_id
                == DonorFacility.facility_id
            )

            .where(
                EmergencySourceMatch.emergency_case_id
                == emergency_case_id
            )

            # Highest ranked donor first
            .order_by(
                EmergencySourceMatch.ranking_score.desc()
            )
        )

        return (
            self.db.execute(query)
            .mappings()
            .all()
        )

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

        self.db.add(
            emergency
        )

        # -------------------------------------------------
        # IMPORTANT:
        # Do NOT commit here.
        #
        # EmergencyService owns the transaction.
        # -------------------------------------------------

        self.db.flush()

        return emergency

    # =====================================================
    # GET ALL EMERGENCIES
    # =====================================================

    def get_all_emergencies(self):

        query = (
            self._base_emergency_query()
        )

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
                        e
                        for e in emergencies
                        if e["emergency_status"]
                        == EmergencyStatusEnum.ACTIVE
                    ]
                ),

            "matching":
                len(
                    [
                        e
                        for e in emergencies
                        if e["emergency_status"]
                        == EmergencyStatusEnum.MATCHING
                    ]
                ),

            "resolved":
                len(
                    [
                        e
                        for e in emergencies
                        if e["emergency_status"]
                        == EmergencyStatusEnum.RESOLVED
                    ]
                ),

            "critical":
                len(
                    [
                        e
                        for e in emergencies
                        if e["severity"]
                        == SeverityEnum.CRITICAL
                    ]
                ),

            "emergency":
                len(
                    [
                        e
                        for e in emergencies
                        if e["severity"]
                        == SeverityEnum.EMERGENCY
                    ]
                )
        }

    # =====================================================
    # CREATE SINGLE SOURCE MATCH
    # =====================================================

    def create_source_match(
        self,
        match_data
    ):

        match = EmergencySourceMatch(
            **match_data
        )

        self.db.add(
            match
        )

        # No commit here.
        # EmergencyService owns the transaction.

        self.db.flush()

        return match

    # =====================================================
    # CREATE MULTIPLE SOURCE MATCHES
    # =====================================================

    def create_source_matches(
        self,
        match_data_list
    ):

        matches = [
            EmergencySourceMatch(
                **match_data
            )
            for match_data in match_data_list
        ]

        self.db.add_all(
            matches
        )

        # No commit here.
        # All matches are committed together
        # with the EmergencyCase and TransferRequest.

        self.db.flush()

        return matches