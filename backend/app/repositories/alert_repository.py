from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.alert import AlertEvent

from app.core.enums import (
    SeverityEnum,
    AlertStatusEnum
)

from app.repositories.base_repository import (
    BaseRepository
)


class AlertRepository(BaseRepository):

    def __init__(self, db: Session):
        super().__init__(db)

    # =====================================================
    # GET ACTIVE ALERTS
    # =====================================================

    def get_active_alerts(self):

        query = (
            select(AlertEvent)
            .where(
                AlertEvent.alert_status ==
                AlertStatusEnum.ACTIVE
            )
        )

        return self.db.execute(query).scalars().all()

    # =====================================================
    # GET CRITICAL ALERTS
    # =====================================================

    def get_critical_alerts(self):

        query = (
            select(AlertEvent)
            .where(
                AlertEvent.severity.in_([
                    SeverityEnum.CRITICAL,
                    SeverityEnum.EMERGENCY
                ])
            )
        )

        return self.db.execute(query).scalars().all()

    # =====================================================
    # GET ALERTS BY FACILITY
    # =====================================================

    def get_alerts_by_facility(
        self,
        facility_id
    ):

        query = (
            select(AlertEvent)
            .where(
                AlertEvent.facility_id == facility_id
            )
        )

        return self.db.execute(query).scalars().all()
    
    # =====================================================
    # CREATE ALERT
    # =====================================================

    def create_alert(
        self,
        alert_data: dict
    ):

        alert = AlertEvent(**alert_data)

        self.db.add(alert)

        self.db.commit()

        self.db.refresh(alert)

        return alert


    # =====================================================
    # GET ALL ALERTS
    # =====================================================

    def get_all_alerts(self):

        query = select(AlertEvent)

        return (
            self.db.execute(query)
            .scalars()
            .all()
        )


    # =====================================================
    # DASHBOARD SUMMARY
    # =====================================================

    def get_alert_dashboard(self):

        alerts = self.get_all_alerts()

        return {

            "total_alerts": len(alerts),

            "active": len(
                [
                    a for a in alerts
                    if a.alert_status
                    ==
                    AlertStatusEnum.ACTIVE
                ]
            ),

            "warning": len(
                [
                    a for a in alerts
                    if a.severity
                    ==
                    SeverityEnum.WARNING
                ]
            ),

            "critical": len(
                [
                    a for a in alerts
                    if a.severity
                    ==
                    SeverityEnum.CRITICAL
                ]
            ),

            "emergency": len(
                [
                    a for a in alerts
                    if a.severity
                    ==
                    SeverityEnum.EMERGENCY
                ]
            )
        }