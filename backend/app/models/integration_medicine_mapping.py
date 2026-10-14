import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class IntegrationMedicineMapping(Base, TimestampMixin):
    """Maps one partner system's medicine key to an AegisFlow medicine."""

    __tablename__ = "integration_medicine_mappings"
    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "external_medicine_code",
            name="uq_integration_medicine_source_external_code",
        ),
    )

    mapping_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("integration_sources.source_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    external_medicine_code: Mapped[str] = mapped_column(String(100), nullable=False)
    medicine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("medicine_master.medicine_id", ondelete="RESTRICT"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
