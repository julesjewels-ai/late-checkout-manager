from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator


class ExtensionRequestCreate(BaseModel):
    booking_id: UUID
    requested_time: datetime

    @field_validator("requested_time")
    def validate_requested_time(cls, v: datetime) -> datetime:
        # Ensure timezone-aware for comparison if needed, or assume UTC
        now = datetime.now(timezone.utc)
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= now:
            raise ValueError("Requested time must be in the future")
        return v


class ExtensionRequestResponse(BaseModel):
    id: UUID
    booking_id: UUID
    requested_time: datetime
    status: str
    price_quote: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
