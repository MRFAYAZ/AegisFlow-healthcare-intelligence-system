from uuid import UUID
from typing import Optional

from pydantic import (
    BaseModel,
    Field
)

from app.schemas.common import (
    BaseSchema
)


# =========================================================
# CREATE MEDICINE
# =========================================================

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

    storage_conditions: str

    standard_lead_time_days: int = 0

    safety_stock_days: int = 3

    unit_price: float = Field(
        ge=0
    )

    expiry_alert_days: int = 30


# =========================================================
# MEDICINE RESPONSE
# =========================================================

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

    unit_price: float