from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.facility import Facility
from app.models.medicine import Medicine
from app.models.inventory import InventoryCurrent
from app.models.alert import AlertEvent
from app.models.emergency import EmergencyCase
from app.models.redistribution import TransferRequest

from app.core.enums import (
    SeverityEnum,
    AlertStatusEnum,
    EmergencyStatusEnum
)


class DashboardRepository:

    def __init__(self, db: Session):

        self.db = db

    def get_dashboard_metrics(self):

        return {

            "facilities":
                self.db.query(Facility).count(),

            "medicines":
                self.db.query(Medicine).count(),

            "inventory_records":
                self.db.query(
                    InventoryCurrent
                ).count(),

            "alerts":
                self.db.query(
                    AlertEvent
                ).count(),

            "active_alerts":
                self.db.query(
                    AlertEvent
                ).filter(
                    AlertEvent.alert_status
                    ==
                    AlertStatusEnum.ACTIVE
                ).count(),

            "emergencies":
                self.db.query(
                    EmergencyCase
                ).count(),

            "active_emergencies":
                self.db.query(
                    EmergencyCase
                ).filter(
                    EmergencyCase.emergency_status.in_(
                        [
                            EmergencyStatusEnum.ACTIVE,
                            EmergencyStatusEnum.MATCHING
                        ]
                    )
                ).count(),

            "transfers":
                self.db.query(
                    TransferRequest
                ).count(),

            "critical_inventory":
                self.db.query(
                    InventoryCurrent
                ).filter(
                    InventoryCurrent.severity.in_(
                        [
                            SeverityEnum.CRITICAL,
                            SeverityEnum.EMERGENCY
                        ]
                    )
                ).count()
        }