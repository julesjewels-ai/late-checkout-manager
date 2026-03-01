from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid

from late_checkout.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False, default="guest")

    bookings = relationship("Booking", back_populates="user")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Uuid, primary_key=True, default=uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    room_number = Column(String, nullable=False)
    original_checkout = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="active")

    user = relationship("User", back_populates="bookings")
    extension_requests = relationship("ExtensionRequest", back_populates="booking")


class ExtensionRequest(Base):
    __tablename__ = "extension_requests"

    id = Column(Uuid, primary_key=True, default=uuid4)
    booking_id = Column(Uuid, ForeignKey("bookings.id"), nullable=False)
    requested_time = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="pending")
    price_quote = Column(Float, nullable=True)

    booking = relationship("Booking", back_populates="extension_requests")
