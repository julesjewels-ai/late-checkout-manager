from datetime import datetime, timezone
from sqlalchemy.orm import Session

from late_checkout.models import User, Booking, ExtensionRequest


def test_database_connection(db_session: Session) -> None:
    # Test that we can query the database
    assert db_session.query(User).count() == 0


def test_create_user(db_session: Session) -> None:
    user = User(name="Test User", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.role == "guest"

    # Cleanup
    db_session.delete(user)
    db_session.commit()


def test_create_booking_and_extension(db_session: Session) -> None:
    user = User(name="Booking User", email="booking@example.com")
    db_session.add(user)
    db_session.commit()

    now = datetime.now(timezone.utc)
    booking = Booking(
        user_id=user.id,
        room_number="101",
        original_checkout=now
    )
    db_session.add(booking)
    db_session.commit()

    extension = ExtensionRequest(
        booking_id=booking.id,
        requested_time=now,
        price_quote=50.0
    )
    db_session.add(extension)
    db_session.commit()

    # Assert relations
    assert len(user.bookings) == 1
    assert user.bookings[0].room_number == "101"
    assert len(booking.extension_requests) == 1
    assert booking.extension_requests[0].price_quote == 50.0

    # Cleanup
    db_session.delete(extension)
    db_session.delete(booking)
    db_session.delete(user)
    db_session.commit()
