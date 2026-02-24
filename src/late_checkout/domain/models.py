from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


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
