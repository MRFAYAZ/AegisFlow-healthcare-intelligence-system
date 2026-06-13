from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.enums import (
    SeverityEnum,
    AlertStatusEnum
)

from app.repositories.alert_repository import (
    AlertRepository
)

from app.repositories.inventory_repository import (
    InventoryRepository
)

from app.repositories.emergency_repository import (
    EmergencyRepository
)


class AlertService:

    def __init__(self, db: Session):

        self.db = db

        self.alert_repository = (
            AlertRepository(db)
        )

        self.inventory_repository = (
            InventoryRepository(db)
        )

        self.emergency_repository = (
            EmergencyRepository(db)
        )

    # =====================================================
    # CREATE SHORTAGE ALERT
    # =====================================================

    def create_shortage_alert(
        self,
        inventory
    ):

        if inventory.severity == SeverityEnum.SAFE:
            return None

        alert_data = {

            "facility_id":
                inventory.facility_id,

            "medicine_id":
                inventory.medicine_id,

            "severity":
                inventory.severity,

            "alert_type":
                "SHORTAGE",

            "alert_message":
                (
                    f"Inventory shortage detected. "
                    f"Current stock: "
                    f"{inventory.available_stock}"
                ),

            "alert_status":
                AlertStatusEnum.ACTIVE
        }

        return (
            self.alert_repository
            .create_alert(alert_data)
        )

    # =====================================================
    # CREATE EXPIRY ALERT
    # =====================================================

    def create_expiry_alert(
        self,
        batch
    ):

        days_remaining = (

            batch.expiry_date

            -

            datetime.utcnow().date()

        ).days

        if days_remaining > 30:
            return None

        severity = SeverityEnum.WARNING

        if days_remaining <= 15:
            severity = SeverityEnum.CRITICAL

        if days_remaining <= 7:
            severity = SeverityEnum.EMERGENCY

        alert_data = {

            "facility_id":
                batch.inventory.facility_id,

            "medicine_id":
                batch.inventory.medicine_id,

            "severity":
                severity,

            "alert_type":
                "EXPIRY",

            "alert_message":
                (
                    f"Batch expires in "
                    f"{days_remaining} days."
                ),

            "alert_status":
                AlertStatusEnum.ACTIVE
        }

        return (
            self.alert_repository
            .create_alert(alert_data)
        )

    # =====================================================
    # CREATE EMERGENCY ALERT
    # =====================================================

    def create_emergency_alert(
        self,
        emergency_case
    ):

        alert_data = {

            "facility_id":
                emergency_case.facility_id,

            "medicine_id":
                emergency_case.medicine_id,

            "severity":
                emergency_case.severity,

            "alert_type":
                "EMERGENCY",

            "alert_message":
                (
                    "Emergency medicine "
                    "shortage reported."
                ),

            "alert_status":
                AlertStatusEnum.ACTIVE
        }

        return (
            self.alert_repository
            .create_alert(alert_data)
        )

    # =====================================================
    # RESOLVE ALERT
    # =====================================================

    def resolve_alert(
        self,
        alert
    ):

        alert.alert_status = (
            AlertStatusEnum.RESOLVED
        )

        alert.resolved_at = (
            datetime.utcnow()
        )

        self.db.commit()

        self.db.refresh(alert)

        return alert

    # =====================================================
    # ESCALATE ALERT
    # =====================================================

    def escalate_alert(
        self,
        alert
    ):

        if (
            alert.severity
            ==
            SeverityEnum.WARNING
        ):
            alert.severity = (
                SeverityEnum.CRITICAL
            )

        elif (
            alert.severity
            ==
            SeverityEnum.CRITICAL
        ):
            alert.severity = (
                SeverityEnum.EMERGENCY
            )

        self.db.commit()

        self.db.refresh(alert)

        return alert

    # =====================================================
    # SYSTEM ALERT SCAN
    # =====================================================

    def run_alert_scan(self):

        inventories = (

            self.inventory_repository
            .get_low_stock_inventory()

        )

        created_alerts = []

        for inventory in inventories:

            alert = (
                self.create_shortage_alert(
                    inventory
                )
            )

            if alert:
                created_alerts.append(
                    alert
                )

        return created_alerts
    
    # =====================================================
    # GET ALL ALERTS
    # =====================================================

    def get_all_alerts(self):

        return (
            self.alert_repository
            .get_all_alerts()
        )


    # =====================================================
    # GET ACTIVE ALERTS
    # =====================================================

    def get_active_alerts(self):

        return (
            self.alert_repository
            .get_active_alerts()
        )


    # =====================================================
    # GET CRITICAL ALERTS
    # =====================================================

    def get_critical_alerts(self):

        return (
            self.alert_repository
            .get_critical_alerts()
        )


    # =====================================================
    # ALERT DASHBOARD
    # =====================================================

    def get_dashboard(self):

        return (
            self.alert_repository
            .get_alert_dashboard()
        )