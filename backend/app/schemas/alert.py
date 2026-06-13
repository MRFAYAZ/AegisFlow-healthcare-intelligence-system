from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from app.core.enums import (
    SeverityEnum,
    AlertStatusEnum
)

from app.schemas.common import (
    BaseSchema
)


# =========================================================
# ALERT RESPONSE
# =========================================================

class AlertResponse(BaseSchema):

    alert_id: UUID

    facility_id: UUID

    medicine_id: UUID

    alert_type: str

    severity: SeverityEnum

    alert_message: str

    alert_status: AlertStatusEnum

    triggered_at: datetime

    resolved_at: datetime | None = None