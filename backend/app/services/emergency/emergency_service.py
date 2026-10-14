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

    def _facility_ids_for_hospital_admin(self, user):
        from app.core.enums import UserRoleEnum
        from app.models.facility_user import FacilityUser
        from sqlalchemy import select

        return list(
            self.db.execute(
                select(FacilityUser.facility_id).where(
                    FacilityUser.user_id == user.user_id,
                    FacilityUser.assigned_role == UserRoleEnum.HOSPITAL_ADMIN,
                )
            ).scalars().all()
        )

    def get_all_emergencies_for_user(self, user):
        from app.core.enums import UserRoleEnum

        if user.role in {UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR}:
            return self.get_all_emergencies()
        if user.role != UserRoleEnum.HOSPITAL_ADMIN:
            raise PermissionError("This role cannot access emergency case records.")

        facility_ids = set(self._facility_ids_for_hospital_admin(user))
        if not facility_ids:
            raise PermissionError("No hospital facility is assigned to this administrator.")
        rows = self.emergency_repository.get_all_emergencies()
        return [
            self._enrich_emergency_response(row)
            for row in rows
            if row["facility_id"] in facility_ids
        ]

    def get_active_emergencies_for_user(self, user):
        from app.core.enums import EmergencyStatusEnum

        return [
            row for row in self.get_all_emergencies_for_user(user)
            if row["emergency_status"] in {
                EmergencyStatusEnum.ACTIVE,
                EmergencyStatusEnum.MATCHING,
            }
        ]

    def get_critical_emergencies_for_user(self, user):
        from app.core.enums import SeverityEnum

        return [
            row for row in self.get_all_emergencies_for_user(user)
            if row["severity"] in {SeverityEnum.CRITICAL, SeverityEnum.EMERGENCY}
        ]

    def get_dashboard_for_user(self, user):
        from app.core.enums import EmergencyStatusEnum, SeverityEnum

        emergencies = self.get_all_emergencies_for_user(user)
        return {
            "total_emergencies": len(emergencies),
            "active": sum(row["emergency_status"] == EmergencyStatusEnum.ACTIVE for row in emergencies),
            "matching": sum(row["emergency_status"] == EmergencyStatusEnum.MATCHING for row in emergencies),
            "partially_resolved": sum(row["emergency_status"] == EmergencyStatusEnum.PARTIALLY_RESOLVED for row in emergencies),
            "resolved": sum(row["emergency_status"] == EmergencyStatusEnum.RESOLVED for row in emergencies),
            "critical": sum(row["severity"] == SeverityEnum.CRITICAL for row in emergencies),
            "emergency": sum(row["severity"] == SeverityEnum.EMERGENCY for row in emergencies),
        }

    def get_timeline_for_emergency(self, emergency_case_id, user) -> dict:
        from app.core.enums import UserRoleEnum
        from app.models.dispatch import TransferDispatch
        from app.models.emergency import EmergencyCase
        from app.models.facility import Facility
        from app.models.facility_user import FacilityUser
        from app.models.redistribution import TransferRequest
        from sqlalchemy import select

        emergency = self.db.get(EmergencyCase, emergency_case_id)
        if emergency is None:
            raise LookupError("Emergency case not found.")

        if user.role == UserRoleEnum.HOSPITAL_ADMIN:
            membership = self.db.execute(
                select(FacilityUser.facility_user_id).where(
                    FacilityUser.user_id == user.user_id,
                    FacilityUser.facility_id == emergency.facility_id,
                    FacilityUser.assigned_role == UserRoleEnum.HOSPITAL_ADMIN,
                )
            ).scalar_one_or_none()
            if membership is None:
                raise PermissionError("Hospital administrators may only view their assigned facility timeline.")
        elif user.role not in {UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR}:
            raise PermissionError("This role cannot view network emergency timelines.")

        events: list[dict] = []

        def add_event(timestamp, event_type: str, title: str, detail: str, transfer_id=None):
            if timestamp is None:
                return
            events.append({
                "_sort": timestamp,
                "timestamp": timestamp.isoformat(),
                "event_type": event_type,
                "title": title,
                "detail": detail,
                "transfer_id": str(transfer_id) if transfer_id else None,
            })

        add_event(
            emergency.triggered_at,
            "EMERGENCY_CREATED",
            "Emergency registered",
            f"{emergency.severity.value} shortage case created for {emergency.required_quantity} target units.",
        )

        query = (
            select(TransferRequest, Facility.facility_name, TransferDispatch)
            .join(Facility, TransferRequest.from_facility_id == Facility.facility_id)
            .outerjoin(TransferDispatch, TransferRequest.transfer_id == TransferDispatch.transfer_id)
            .where(TransferRequest.emergency_case_id == emergency_case_id)
            .order_by(TransferRequest.requested_at.asc())
        )
        for transfer, donor_name, dispatch in self.db.execute(query).all():
            transfer_id = transfer.transfer_id
            add_event(
                transfer.requested_at,
                "TRANSFER_REQUESTED",
                "Supply request created",
                f"{transfer.requested_quantity} units requested from {donor_name}.",
                transfer_id,
            )

            if transfer.approved_at is not None:
                if transfer.transfer_status.value == "REJECTED":
                    decision_detail = transfer.rejection_reason or "The destination facility rejected this transfer request."
                    add_event(
                        transfer.approved_at,
                        "TRANSFER_REJECTED",
                        "Hospital rejected transfer",
                        decision_detail,
                        transfer_id,
                    )
                else:
                    add_event(
                        transfer.approved_at,
                        "TRANSFER_APPROVED",
                        "Hospital decision recorded",
                        f"{transfer.approved_quantity or 0} units approved.",
                        transfer_id,
                    )

            if dispatch is not None:
                add_event(
                    dispatch.created_at,
                    "DISPATCH_ASSIGNED",
                    "Transport assigned",
                    f"{dispatch.transport_type}"
                    + (f" — {dispatch.vehicle_reference}" if dispatch.vehicle_reference else ""),
                    transfer_id,
                )
                add_event(
                    dispatch.dispatched_at,
                    "SHIPMENT_DISPATCHED",
                    "Shipment dispatched",
                    f"Transfer entered transit using {dispatch.transport_type}.",
                    transfer_id,
                )
                add_event(
                    dispatch.delivered_at,
                    "SHIPMENT_DELIVERED",
                    "Delivery confirmed",
                    f"{transfer.approved_quantity or 0} units delivered to the destination facility.",
                    transfer_id,
                )

        if emergency.resolved_at is not None:
            add_event(
                emergency.resolved_at,
                "EMERGENCY_RESOLVED",
                "Emergency resolved",
                "The emergency target quantity was met.",
            )

        events.sort(key=lambda event: event["_sort"])
        for event in events:
            event.pop("_sort", None)

        return {
            "emergency_case_id": str(emergency_case_id),
            "timeline_scope": "timestamps currently stored on emergency, transfer and dispatch records",
            "events": events,
        }

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
            max_distance_km=(
                max_distance_km
                if max_distance_km is not None
                else emergency.emergency_radius_km
            ),
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