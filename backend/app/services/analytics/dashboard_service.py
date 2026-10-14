from sqlalchemy.orm import Session

from sqlalchemy import func, select

from app.models.redistribution import TransferRequest

from app.models.inventory import (
    InventoryCurrent
)

from app.models.alert import (
    AlertEvent
)

from app.models.emergency import (
    EmergencyCase
)

from app.models.facility import (
    Facility
)

from app.models.medicine import (
    Medicine
)

from app.core.enums import (
    SeverityEnum,
    AlertStatusEnum,
    EmergencyStatusEnum,
    TransferStatusEnum,
    UserRoleEnum,
)
from app.models.facility_user import FacilityUser


class DashboardService:

    def __init__(self, db: Session):

        self.db = db

    # =====================================================
    # SYSTEM OVERVIEW METRICS
    # =====================================================

    def get_system_overview(self):

        total_facilities = (
            self.db.execute(
                select(func.count())
                .select_from(Facility)
            )
            .scalar()
        )

        total_medicines = (
            self.db.execute(
                select(func.count())
                .select_from(Medicine)
            )
            .scalar()
        )

        total_inventory_records = (
            self.db.execute(
                select(func.count())
                .select_from(
                    InventoryCurrent
                )
            )
            .scalar()
        )

        return {
            "total_facilities":
                total_facilities,

            "total_medicines":
                total_medicines,

            "total_inventory_records":
                total_inventory_records
        }

    # =====================================================
    # INVENTORY HEALTH SUMMARY
    # =====================================================

    def get_inventory_health_summary(self):

        safe_count = {
            self.db.execute(
                select(func.count())
                .where(
                    InventoryCurrent.severity ==
                    SeverityEnum.SAFE
                )
            )
            .scalar()
        }

        warning_count = (
            self.db.execute(
                select(func.count())
                .where(
                    InventoryCurrent.severity ==
                    SeverityEnum.WARNING
                )
            )
            .scalar()
        )

        critical_count = (
            self.db.execute(
                select(func.count())
                .where(
                    InventoryCurrent.severity ==
                    SeverityEnum.CRITICAL
                )
            )
            .scalar()
        )

        emergency_count = (
            self.db.execute(
                select(func.count())
                .where(
                    InventoryCurrent.severity ==
                    SeverityEnum.EMERGENCY
                )
            )
            .scalar()
        )

        return {

            "safe_inventory":
                safe_count,

            "warning_inventory":
                warning_count,

            "critical_inventory":
                critical_count,

            "emergency_inventory":
                emergency_count
        }

    # =====================================================
    # ALERT SUMMARY
    # =====================================================

    def get_alert_summary(self):

        active_alerts = (
            self.db.execute(
                select(func.count())
                .where(
                    AlertEvent.alert_status ==
                    AlertStatusEnum.ACTIVE
                )
            )
            .scalar()
        )

        return {
            "active_alerts":
                active_alerts
        }

    # =====================================================
    # EMERGENCY SUMMARY
    # =====================================================

    def get_emergency_summary(self):

        active_emergencies = (
            self.db.execute(
                select(func.count())
                .where(
                    EmergencyCase
                    .emergency_status
                    .in_([
                        EmergencyStatusEnum.ACTIVE,
                        EmergencyStatusEnum.MATCHING
                    ])
                )
            )
            .scalar()
        )

        return {
            "active_emergencies":
                active_emergencies
        }

    # =====================================================
    # COMPLETE DASHBOARD SNAPSHOT
    # =====================================================

    def get_dashboard_snapshot(self):

        return {

            "system_overview":
                self.get_system_overview(),

            "inventory_health":
                self.get_inventory_health_summary(),

            "alerts":
                self.get_alert_summary(),

            "emergencies":
                self.get_emergency_summary()
        }

    # =====================================================
    # TRANSFER SUMMARY
    # =====================================================

    def get_transfer_summary(self):

        total_transfers = (
            self.db.execute(
                select(func.count())
                .select_from(
                    TransferRequest
                )
            )
            .scalar()
        )

        pending_transfers = (
            self.db.execute(
                select(func.count())
                .where(
                    TransferRequest.transfer_status
                    ==
                    TransferStatusEnum.PENDING
                )
            )
            .scalar()
        )

        completed_transfers = (
            self.db.execute(
                select(func.count())
                .where(
                    TransferRequest.transfer_status
                    ==
                    TransferStatusEnum.COMPLETED
                )
            )
            .scalar()
        )

        return {

            "total_transfers":
                total_transfers,

            "pending_transfers":
                pending_transfers,

            "completed_transfers":
                completed_transfers
        }
    
    # =====================================================
    # REVIEW DASHBOARD
    # =====================================================

    def get_review_dashboard(self):

        overview = self.get_system_overview()

        inventory = (
            self.get_inventory_health_summary()
        )

        alerts = (
            self.get_alert_summary()
        )

        emergencies = (
            self.get_emergency_summary()
        )

        transfers = (
            self.get_transfer_summary()
        )

        return {

            "facilities":
                overview[
                    "total_facilities"
                ],

            "medicines":
                overview[
                    "total_medicines"
                ],

            "inventory_records":
                overview[
                    "total_inventory_records"
                ],

            "safe_inventory":
                inventory[
                    "safe_inventory"
                ],

            "warning_inventory":
                inventory[
                    "warning_inventory"
                ],
            
            "critical_inventory":
                inventory[
                    "critical_inventory"
                ],

            "emergency_inventory":
                inventory[
                    "emergency_inventory"
                ],

            "active_alerts":
                alerts[
                    "active_alerts"
                ],

            "active_emergencies":
                emergencies[
                    "active_emergencies"
                ],

            "total_transfers":
                transfers[
                    "total_transfers"
                ]
        }

    def get_dashboard_for_user(self, user):
        """Expose global metrics to operations roles and facility metrics to facility users."""
        if user.role in {UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.EMERGENCY_OPERATOR}:
            return self.get_review_dashboard()

        if user.role not in {
            UserRoleEnum.HOSPITAL_ADMIN,
            UserRoleEnum.PHARMACIST,
            UserRoleEnum.SHOP_OWNER,
            UserRoleEnum.SUPPLIER,
        }:
            raise PermissionError("This role cannot access dashboard metrics.")

        facility_ids = self.db.execute(
            select(FacilityUser.facility_id).where(
                FacilityUser.user_id == user.user_id
            )
        ).scalars().all()
        if not facility_ids:
            raise PermissionError("No facility is assigned to this user.")

        scope = InventoryCurrent.facility_id.in_(facility_ids)
        facility_filter = Facility.facility_id.in_(facility_ids)
        alert_filter = AlertEvent.facility_id.in_(facility_ids)
        emergency_filter = EmergencyCase.facility_id.in_(facility_ids)
        transfer_filter = (
            TransferRequest.from_facility_id.in_(facility_ids)
            | TransferRequest.to_facility_id.in_(facility_ids)
        )

        def count(query):
            return int(self.db.execute(query).scalar_one() or 0)

        total_facilities = count(
            select(func.count()).select_from(Facility).where(facility_filter)
        )
        total_medicines = count(
            select(func.count(func.distinct(InventoryCurrent.medicine_id)))
            .select_from(InventoryCurrent).where(scope)
        )
        total_inventory = count(
            select(func.count()).select_from(InventoryCurrent).where(scope)
        )
        safe = count(
            select(func.count()).select_from(InventoryCurrent).where(
                scope, InventoryCurrent.severity == SeverityEnum.SAFE
            )
        )
        warning = count(
            select(func.count()).select_from(InventoryCurrent).where(
                scope, InventoryCurrent.severity == SeverityEnum.WARNING
            )
        )
        critical = count(
            select(func.count()).select_from(InventoryCurrent).where(
                scope, InventoryCurrent.severity == SeverityEnum.CRITICAL
            )
        )
        emergency_stock = count(
            select(func.count()).select_from(InventoryCurrent).where(
                scope, InventoryCurrent.severity == SeverityEnum.EMERGENCY
            )
        )
        active_alerts = count(
            select(func.count()).select_from(AlertEvent).where(
                alert_filter, AlertEvent.alert_status == AlertStatusEnum.ACTIVE
            )
        )
        active_emergencies = count(
            select(func.count()).select_from(EmergencyCase).where(
                emergency_filter,
                EmergencyCase.emergency_status.in_([
                    EmergencyStatusEnum.ACTIVE,
                    EmergencyStatusEnum.MATCHING,
                ]),
            )
        )
        total_transfers = count(
            select(func.count()).select_from(TransferRequest).where(transfer_filter)
        )

        return {
            "facilities": total_facilities,
            "medicines": total_medicines,
            "inventory_records": total_inventory,
            "safe_inventory": safe,
            "warning_inventory": warning,
            "critical_inventory": critical,
            "emergency_inventory": emergency_stock,
            "active_alerts": active_alerts,
            "active_emergencies": active_emergencies,
            "total_transfers": total_transfers,
        }

    def get_dashboard_snapshot_for_user(self, user):
        review = self.get_dashboard_for_user(user)
        return {
            "system_overview": {
                "total_facilities": review["facilities"],
                "total_medicines": review["medicines"],
                "total_inventory_records": review["inventory_records"],
            },
            "inventory_health": {
                "safe_inventory": review["safe_inventory"],
                "warning_inventory": review["warning_inventory"],
                "critical_inventory": review["critical_inventory"],
                "emergency_inventory": review["emergency_inventory"],
            },
            "alerts": {"active_alerts": review["active_alerts"]},
            "emergencies": {"active_emergencies": review["active_emergencies"]},
        }
