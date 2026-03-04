from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ExtensionRequestCreate(BaseModel):
    booking_id: UUID
    requested_time: datetime


class ExtensionRequestResponse(BaseModel):
    id: UUID
    booking_id: UUID
    requested_time: datetime
    status: str
    price_quote: Optional[float] = None
