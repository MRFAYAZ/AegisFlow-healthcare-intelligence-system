from uuid import UUID

from pydantic import BaseModel, Field
from app.schemas.common import BaseSchema


class MedicineCreate(BaseModel):
    medicine_code: str
    medicine_name: str
    generic_name: str
    category: str
    dosage_form: str
    strength: str
    manufacturer: str
    prescription_required: bool = False
    is_critical: bool = False
    requires_cold_chain: bool = False
    storage_conditions: str
    standard_lead_time_days: int = Field(default=0, ge=0)
    safety_stock_days: int = Field(default=3, ge=0)
    unit_price: float = Field(ge=0)
    expiry_alert_days: int = Field(default=30, ge=0)


class MedicineResponse(BaseSchema):
    medicine_id: UUID
    medicine_code: str
    medicine_name: str
    generic_name: str
    category: str
    dosage_form: str
    strength: str
    manufacturer: str
    prescription_required: bool
    is_critical: bool
    requires_cold_chain: bool = False
    unit_price: float
