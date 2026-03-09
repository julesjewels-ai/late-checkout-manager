from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExtensionRequestCreate(BaseModel):
    booking_id: UUID
    requested_time: datetime


class ExtensionRequestResponse(BaseModel):
    id: UUID
    booking_id: UUID
    requested_time: datetime
    status: str
    price_quote: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
