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
    TransferStatusEnum
)


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