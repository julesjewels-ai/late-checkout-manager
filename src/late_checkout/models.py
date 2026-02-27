from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.types import Uuid
from sqlalchemy.orm import relationship

from late_checkout.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, default="guest", nullable=False)

    bookings = relationship("Booking", back_populates="user")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Uuid, primary_key=True)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    room_number = Column(String, nullable=False)
    original_checkout = Column(DateTime, nullable=False)
    status = Column(String, default="active", nullable=False)

    user = relationship("User", back_populates="bookings")
    extension_requests = relationship("ExtensionRequest", back_populates="booking")


class ExtensionRequest(Base):
    __tablename__ = "extension_requests"

    id = Column(Uuid, primary_key=True)
    booking_id = Column(Uuid, ForeignKey("bookings.id"), nullable=False)
    requested_time = Column(DateTime, nullable=False)
    status = Column(String, default="pending", nullable=False)
    price_quote = Column(Float, nullable=True)

    booking = relationship("Booking", back_populates="extension_requests")
