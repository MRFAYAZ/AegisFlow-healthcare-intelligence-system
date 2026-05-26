import uuid

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    Enum,
    TIMESTAMP
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, TimestampMixin

from app.core.enums import (
    SeverityEnum,
    AlertStatusEnum
)


# =========================================================
# ALERT EVENT
# =========================================================

class AlertEvent(Base, TimestampMixin):
    __tablename__ = "alert_events"

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    facility_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("facilities.facility_id"),
        nullable=False
    )

    medicine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("medicine_master.medicine_id"),
        nullable=False
    )

    alert_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    severity: Mapped[SeverityEnum] = mapped_column(
        Enum(SeverityEnum),
        nullable=False
    )

    alert_message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    alert_status: Mapped[AlertStatusEnum] = mapped_column(
        Enum(AlertStatusEnum),
        default=AlertStatusEnum.ACTIVE
    )

    triggered_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True)
    )

    resolved_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True)
    )

    facility = relationship("Facility")

    medicine = relationship("Medicine")