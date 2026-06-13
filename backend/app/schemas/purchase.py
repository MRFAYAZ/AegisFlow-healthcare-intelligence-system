from uuid import UUID
from datetime import datetime

from pydantic import (
    BaseModel,
    Field
)

from app.core.enums import (
    PurchaseStatusEnum
)

from app.schemas.common import (
    BaseSchema
)


# =========================================================
# CREATE PURCHASE
# =========================================================

class PurchaseCreate(BaseModel):

    facility_id: UUID

    medicine_id: UUID

    customer_name: str

    customer_phone: str

    quantity: int = Field(
        gt=0
    )

    unit_price: float = Field(
        ge=0
    )


# =========================================================
# PURCHASE RESPONSE
# =========================================================

class PurchaseResponse(BaseSchema):

    purchase_id: UUID

    facility_id: UUID

    medicine_id: UUID

    customer_name: str

    quantity: int

    unit_price: float

    total_amount: float

    purchase_status: PurchaseStatusEnum

    stock_reduced: bool

    purchased_at: datetime