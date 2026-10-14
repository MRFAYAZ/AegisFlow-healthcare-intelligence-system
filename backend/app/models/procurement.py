import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, TIMESTAMP, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SeverityEnum, SupplyRequestStatusEnum
from app.models.base import Base, TimestampMixin


class ReplenishmentRequirement(Base, TimestampMixin):
    __tablename__ = "replenishment_requirements"

    requirement_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.facility_id"), nullable=False)
    medicine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("medicine_master.medicine_id"), nullable=False)
    requested_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[SeverityEnum] = mapped_column(Enum(SeverityEnum), nullable=False)
    required_by: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True))
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="OPEN", nullable=False)

    facility = relationship("Facility")
    medicine = relationship("Medicine")


class SupplyRequest(Base, TimestampMixin):
    __tablename__ = "supply_requests"

    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requirement_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("replenishment_requirements.requirement_id"), nullable=False)
    supplier_facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.facility_id"), nullable=False)
    target_facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.facility_id"), nullable=False)
    medicine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("medicine_master.medicine_id"), nullable=False)
    requested_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    accepted_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    recommendation_score: Mapped[float] = mapped_column(DECIMAL(6, 2), nullable=False)
    status: Mapped[SupplyRequestStatusEnum] = mapped_column(Enum(SupplyRequestStatusEnum), default=SupplyRequestStatusEnum.PENDING_APPROVAL, nullable=False)
    response_note: Mapped[str | None] = mapped_column(Text)
    responded_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True))

    requirement = relationship("ReplenishmentRequirement")
    supplier = relationship("Facility", foreign_keys=[supplier_facility_id])
    target = relationship("Facility", foreign_keys=[target_facility_id])
    medicine = relationship("Medicine")