import uuid
from datetime import datetime, timedelta
import pytest
from pydantic import ValidationError
from late_checkout.domain.models import User, Booking, ExtensionRequest


def test_user_creation() -> None:
    user_id = uuid.uuid4()
    user = User(id=user_id, name="John Doe", email="john@example.com")
    assert user.id == user_id
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    assert user.role == "guest"


def test_user_invalid_email() -> None:
    user_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        User(id=user_id, name="John Doe", email="not-an-email")


def test_booking_creation() -> None:
    booking_id = uuid.uuid4()
    user_id = uuid.uuid4()
    original_checkout = datetime.now()
    booking = Booking(
        id=booking_id,
        user_id=user_id,
        room_number="101",
        original_checkout=original_checkout
    )
    assert booking.id == booking_id
    assert booking.user_id == user_id
    assert booking.room_number == "101"
    assert booking.status == "active"


def test_extension_request_creation() -> None:
    request_id = uuid.uuid4()
    booking_id = uuid.uuid4()
    requested_time = datetime.now() + timedelta(hours=2)
    request = ExtensionRequest(
        id=request_id,
        booking_id=booking_id,
        requested_time=requested_time
    )
    assert request.id == request_id
    assert request.booking_id == booking_id
    assert request.status == "pending"
    assert request.price_quote is None


def test_extension_request_with_price() -> None:
    request_id = uuid.uuid4()
    booking_id = uuid.uuid4()
    requested_time = datetime.now() + timedelta(hours=2)
    request = ExtensionRequest(
        id=request_id,
        booking_id=booking_id,
        requested_time=requested_time,
        price_quote=50.0
    )
    assert request.price_quote == 50.0
