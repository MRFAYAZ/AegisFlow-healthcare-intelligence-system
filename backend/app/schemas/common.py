from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# =========================================================
# BASE RESPONSE SCHEMA
# =========================================================

class BaseSchema(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# TIMESTAMP RESPONSE MIXIN
# =========================================================

class TimestampSchema(BaseSchema):

    created_at: datetime

    updated_at: datetime


# =========================================================
# UUID RESPONSE MIXIN
# =========================================================

class UUIDSchema(BaseSchema):

    id: UUID