from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.services.emergency.matching_service import (
    MatchingService
)

from app.repositories.emergency_repository import (
    EmergencyRepository
)

from app.repositories.redistribution_repository import (
    RedistributionRepository
)

from app.core.enums import (
    TransferStatusEnum,
    EmergencyStatusEnum
)

from app.models.emergency import EmergencyCase
from app.services.governance.audit_service import AuditService


class EmergencyService:

    def __init__(self, db: Session):

        self.db = db

        self.emergency_repository = (
            EmergencyRepository(db)
        )

        self.redistribution_repository = (
            RedistributionRepository(db)
        )

        self.matching_service = (
            MatchingService(db)
        )

    # =====================================================
    # ENRICH EMERGENCY RESPONSE
    # =====================================================

    def _enrich_emergency_response(
        self,
        emergency_row: dict
    ) -> dict:

        payload = dict(emergency_row)

        transfer_status = payload.get(
            "transfer_status"
        )

        # -------------------------------------------------
        # No transfer yet
        # -------------------------------------------------

        if transfer_status is None:

            payload["cascade_safe"] = None
            payload["estimated_eta_minutes"] = None
            payload["ai_reason"] = None
            payload["alternative_donors"] = None

            return payload

        # -------------------------------------------------
        # Estimated ETA
        # -------------------------------------------------

        distance_km = payload.get(
            "transfer_distance_km"
        )

        eta_minutes = None

        if distance_km is not None:

            distance_value = float(
                distance_km
            )

            eta_minutes = max(
                10,
                int(
                    round(
                        distance_value * 2.2
                    )
                )
            )

        # -------------------------------------------------
        # Recommendation reason
        # -------------------------------------------------

        ai_reason = payload.get(
            "recommendation_reason"
        )

        if not ai_reason:

            ai_reason = (
                "Highest inventory with minimum "
                "delivery distance."
            )

        # -------------------------------------------------
        # Alternative donors
        # -------------------------------------------------

        alternative_donors = payload.get(
            "alternative_donors"
        )

        if alternative_donors is None:

            if transfer_status in {
                TransferStatusEnum.PENDING,
                TransferStatusEnum.APPROVED,
                TransferStatusEnum.IN_TRANSIT,
            }:

                alternative_donors = 4

            else:

                alternative_donors = 2

        # -------------------------------------------------
        # Final enriched payload
        # -------------------------------------------------

        payload["cascade_safe"] = (
            payload.get("cascade_safe")
        )

        payload["estimated_eta_minutes"] = (
            eta_minutes
        )

        payload["ai_reason"] = (
            ai_reason
        )

        payload["alternative_donors"] = (
            alternative_donors
        )

        return payload

    # =====================================================
    # CREATE EMERGENCY
    # =====================================================

    def create_emergency(
        self,
        emergency_data: dict
    ):

        try:

            # =============================================
            # 1. CREATE EMERGENCY CASE
            # =============================================

            emergency = (
                self.emergency_repository
                .create_emergency_case(
                    emergency_data
                )
            )

            AuditService(self.db).record_event(
                action_type="EMERGENCY_CREATED",
                entity_type="EMERGENCY",
                entity_id=emergency.emergency_case_id,
                new_value={
                    "required_quantity": emergency.required_quantity,
                    "severity": emergency.severity.value,
                },
            )

            # =============================================
            # 2. FIND AND RANK DONORS
            # =============================================

            ranked_candidates = (
                self.matching_service
                .find_emergency_sources(

                    medicine_id=(
                        emergency.medicine_id
                    ),

                    requesting_facility_id=(
                        emergency.facility_id
                    ),

                    requested_quantity=(
                        emergency.required_quantity
                    )
                )
            )

            # =============================================
            # 3. NO ELIGIBLE DONOR
            # =============================================

            if not ranked_candidates:

                # Emergency remains ACTIVE because
                # no donor has been identified yet.

                self.db.commit()

                return {
                    "emergency": emergency,
                    "recommended_sources": []
                }

            # =============================================
            # 4. PERSIST ALL SOURCE MATCHES
            # =============================================

            matched_at = datetime.now(
                timezone.utc
            )

            AuditService(self.db).record_event(
                action_type="DONOR_MATCHING_COMPLETED",
                entity_type="EMERGENCY",
                entity_id=emergency.emergency_case_id,
                new_value={"candidate_count": len(ranked_candidates)},
            )

            match_records = []

            for index, candidate in enumerate(
                ranked_candidates
            ):

                match_records.append({

                    "emergency_case_id":
                        emergency.emergency_case_id,

                    "source_facility_id":
                        candidate["facility_id"],

                    "medicine_id":
                        emergency.medicine_id,

                    "available_quantity":
                        candidate[
                            "available_quantity"
                        ],

                    "transferable_quantity":
                        candidate[
                            "available_quantity"
                        ],

                    "selected_batch_number": candidate.get("selected_batch_number"),
                    "earliest_expiry_date": candidate.get("earliest_expiry_date"),
                    "cold_chain_required": candidate.get("cold_chain_required", False),
                    "cold_chain_capable": candidate.get("cold_chain_capable", False),
                    "safety_status": candidate.get("safety_status", "LEGACY_UNVALIDATED"),
                    "safety_reason": candidate.get("safety_reason"),
                    "batch_allocations": candidate.get("batch_allocations", []),

                    "distance_km":
                        candidate[
                            "distance_km"
                        ],

                    "donor_shortage_score":
                        candidate.get(
                            "donor_shortage_score",
                            0
                        ),

                    "distance_score":
                        candidate[
                            "distance_score"
                        ],

                    "inventory_score":
                        candidate[
                            "inventory_score"
                        ],

                    "donor_health_score":
                        candidate[
                            "donor_health_score"
                        ],

                    "ranking_score":
                        candidate[
                            "ranking_score"
                        ],

                    "is_selected":
                        index == 0,

                    "matched_at":
                        matched_at
                })

            matches = (
                self.emergency_repository
                .create_source_matches(
                    match_records
                )
            )

            # =============================================
            # 5. SELECT BEST DONOR
            # =============================================

            selected_candidate = (
                ranked_candidates[0]
            )

            # Quantity that the matching engine
            # recommends for the transfer.
            #
            # IMPORTANT:
            # This is NOT the approved quantity.
            # Hospital Admin approval happens later.

            transfer_quantity = min(

                emergency.required_quantity,

                selected_candidate[
                    "available_quantity"
                ]
            )

            # =============================================
            # 6. CREATE PENDING TRANSFER
            # =============================================

            transfer_data = {

                "from_facility_id":
                    selected_candidate[
                        "facility_id"
                    ],

                "to_facility_id":
                    emergency.facility_id,

                "medicine_id":
                    emergency.medicine_id,

                "emergency_case_id":
                    emergency.emergency_case_id,

                "requested_quantity":
                    transfer_quantity,

                # Approval has NOT happened yet.
                "approved_quantity":
                    None,

                "transfer_status":
                    TransferStatusEnum.PENDING,

                # Current domain rule:
                # donor was considered safe during matching.
                #
                # Final safety validation must still happen
                # when the transfer is actually approved.
                "cascade_safe":
                    True,

                "match_score":
                    selected_candidate[
                        "ranking_score"
                    ],

                "transfer_distance_km":
                    selected_candidate[
                        "distance_km"
                    ],

                "recommendation_reason":
                    (
                        "Highest-ranked eligible donor "
                        "based on inventory availability, "
                        "geographic distance, and donor safety."
                    )
            }

            transfer = (
                self.redistribution_repository
                .create_transfer_request(
                    transfer_data
                )
            )

            # =============================================
            # 7. MOVE EMERGENCY INTO MATCHING STATE
            # =============================================

            emergency.emergency_status = (
                EmergencyStatusEnum.MATCHING
            )

            # =============================================
            # 8. COMMIT COMPLETE TRANSACTION
            # =============================================
            #
            # The repositories should NOT commit
            # individually.
            #
            # Everything created above is committed
            # together here.
            #

            self.db.commit()

            # =============================================
            # 9. REFRESH PERSISTED OBJECTS
            # =============================================

            self.db.refresh(
                emergency
            )

            self.db.refresh(
                transfer
            )

            # =============================================
            # 10. RETURN RESULT
            # =============================================

            return {

                "emergency":
                    emergency,

                "recommended_sources":
                    ranked_candidates,

                "transfer":
                    transfer
            }

        except Exception:

            # =============================================
            # ROLLBACK COMPLETE TRANSACTION
            # =============================================

            self.db.rollback()

            raise

    # =====================================================
    # GET ALL EMERGENCIES
    # =====================================================

    def get_all_emergencies(self):

        emergencies = (
            self.emergency_repository
            .get_all_emergencies()
        )

        return [
            self._enrich_emergency_response(
                emergency
            )
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
            self._enrich_emergency_response(
                emergency
            )
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
            self._enrich_emergency_response(
                emergency
            )
            for emergency in emergencies
        ]

    # =====================================================
    # DASHBOARD
    # =====================================================

    def update_emergency_fulfillment(
        self,
        emergency_case_id,
    ):
        emergency = (
            self.db.query(EmergencyCase)
            .filter(
                EmergencyCase.emergency_case_id == emergency_case_id
            )
            .with_for_update()
            .first()
        )

        if emergency is None:
            raise ValueError("Emergency case not found.")

        previous_status = emergency.emergency_status
        delivered_quantity = (
            self.emergency_repository
            .get_completed_transfer_quantity(
                emergency_case_id
            )
        )

        required_quantity = emergency.required_quantity or 0

        if delivered_quantity >= required_quantity:
            emergency.emergency_status = EmergencyStatusEnum.RESOLVED
            emergency.resolved_at = datetime.now(timezone.utc)
        elif delivered_quantity > 0:
            emergency.emergency_status = EmergencyStatusEnum.PARTIALLY_RESOLVED

        if emergency.emergency_status != previous_status:
            AuditService(self.db).record_event(
                action_type=(
                    "EMERGENCY_RESOLVED"
                    if emergency.emergency_status == EmergencyStatusEnum.RESOLVED
                    else "EMERGENCY_PARTIALLY_RESOLVED"
                ),
                entity_type="EMERGENCY",
                entity_id=emergency_case_id,
                new_value={
                    "status": emergency.emergency_status.value,
                    "delivered_quantity": delivered_quantity,
                    "required_quantity": required_quantity,
                },
            )

        self.db.flush()

        return emergency

    def get_dashboard(self):

        return (
            self.emergency_repository
            .get_emergency_dashboard()
        )

    # =====================================================
    # GET EMERGENCY MATCHES
    # =====================================================

    def get_matches(
        self,
        emergency_case_id
    ):

        return (
            self.emergency_repository
            .get_matches_for_emergency(
                emergency_case_id
            )
        )