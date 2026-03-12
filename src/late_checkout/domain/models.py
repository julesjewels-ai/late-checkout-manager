from uuid import UUID
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class User(BaseModel):
    id: UUID
    name: str = Field(..., min_length=1)
    email: EmailStr
    role: str = Field(default="guest")


class Booking(BaseModel):
    id: UUID
    user_id: UUID
    room_number: str
    original_checkout: datetime
    status: str = Field(default="active")


class ExtensionRequest(BaseModel):
    id: UUID
    booking_id: UUID
    requested_time: datetime
    status: str = Field(default="pending")
    price_quote: Optional[float] = None


class ExtensionRequestCreate(BaseModel):
    booking_id: UUID
    requested_time: datetime

    @field_validator("requested_time")
    def validate_requested_time(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("requested_time must be timezone-aware")
        if v < datetime.now(timezone.utc):
            raise ValueError("requested_time must be in the future")
        return v
