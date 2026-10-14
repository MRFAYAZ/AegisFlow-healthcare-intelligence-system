import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class IntegrationSource(Base, TimestampMixin):
    """One authenticated external-system connection restricted to one facility."""

    __tablename__ = "integration_sources"
    __table_args__ = (
        UniqueConstraint("facility_id", name="uq_integration_source_facility"),
    )

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    system_type: Mapped[str] = mapped_column(String(80), nullable=False)
    facility_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("facilities.facility_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    credential_hash: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    last_snapshot_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
