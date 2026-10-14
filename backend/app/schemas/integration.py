from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class IntegrationSourceCreate(BaseModel):
    source_name: str = Field(min_length=3, max_length=255)
    system_type: str = Field(min_length=2, max_length=80)
    facility_id: UUID

    @field_validator("source_name", "system_type", mode="before")
    @classmethod
    def strip_source_text(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip()


class IntegrationSourceCreated(BaseModel):
    source_id: UUID
    source_name: str
    system_type: str
    facility_id: UUID
    is_active: bool
    integration_key: str
    credential_note: str


class IntegrationSourceResponse(BaseModel):
    source_id: UUID
    source_name: str
    system_type: str
    facility_id: UUID
    is_active: bool
    last_snapshot_at: datetime | None = None


class IntegrationMedicineMappingCreate(BaseModel):
    external_medicine_code: str = Field(min_length=1, max_length=100)
    medicine_id: UUID


class IntegrationMedicineMappingResponse(BaseModel):
    mapping_id: UUID
    source_id: UUID
    external_medicine_code: str
    medicine_id: UUID
    is_active: bool


class IntegrationBatchSnapshot(BaseModel):
    batch_number: str = Field(min_length=1, max_length=100)
    
    @field_validator("batch_number", mode="before")
    @classmethod
    def strip_batch_number(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip()
    manufacturing_date: date
    expiry_date: date
    quantity_received: int = Field(ge=0)
    available_stock: int = Field(ge=0, description="Source-reported available stock before AegisFlow reservations.")
    reserved_stock: int = Field(ge=0, description="Reservations external to AegisFlow.")
    supplier_name: str = Field(default="Unknown source", max_length=255)
    unit_cost: Decimal = Field(default=Decimal("0"), ge=0)

    @model_validator(mode="after")
    def validate_lot_quantity(self):
        if self.quantity_received < self.available_stock + self.reserved_stock:
            raise ValueError("quantity_received cannot be less than current available plus reserved lot stock.")
        if self.expiry_date < self.manufacturing_date:
            raise ValueError("expiry_date cannot precede manufacturing_date.")
        return self


class IntegrationInventoryItem(BaseModel):
    external_medicine_code: str = Field(min_length=1, max_length=100)
    total_stock: int = Field(ge=0)
    minimum_threshold: int = Field(ge=0)
    reorder_threshold: int = Field(ge=0)
    daily_consumption_rate: Decimal = Field(ge=0)
    lead_time_days: int = Field(ge=0)
    batches: list[IntegrationBatchSnapshot] = Field(default_factory=list)

    @field_validator("external_medicine_code", mode="before")
    @classmethod
    def strip_external_medicine_code(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip()

    @model_validator(mode="after")
    def validate_snapshot_batches(self):
        if self.total_stock > 0 and not self.batches:
            raise ValueError("Non-zero inventory snapshots require batch-level expiry data.")
        codes = [batch.batch_number for batch in self.batches]
        if len(codes) != len(set(codes)):
            raise ValueError("batch_number values must be unique within a medicine snapshot.")
        lot_stock = sum(batch.available_stock + batch.reserved_stock for batch in self.batches)
        if lot_stock != self.total_stock:
            raise ValueError(
                "total_stock must equal the sum of source-reported available and reserved stock across batches."
            )
        return self


class IntegrationInventorySnapshotRequest(BaseModel):
    external_event_id: str = Field(min_length=1, max_length=255)
    source_timestamp: datetime
    items: list[IntegrationInventoryItem] = Field(min_length=1, max_length=500)

    @field_validator("external_event_id", mode="before")
    @classmethod
    def strip_external_event_id(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        return value.strip()

    @field_validator("source_timestamp")
    @classmethod
    def require_timezone_aware_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("source_timestamp must include a timezone offset.")
        return value

    @model_validator(mode="after")
    def require_unique_medicine_lines(self):
        codes = [item.external_medicine_code for item in self.items]
        if len(codes) != len(set(codes)):
            raise ValueError("Each external_medicine_code must appear once per snapshot.")
        return self


class IntegrationSnapshotResponse(BaseModel):
    accepted: bool
    idempotent_replay: bool
    source_id: UUID
    external_event_id: str
    source_timestamp: datetime
    records_processed: int
    message: str
