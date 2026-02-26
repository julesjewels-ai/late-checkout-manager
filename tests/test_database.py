from typing import Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from late_checkout.core.database import Base
from late_checkout.models import User, Booking, ExtensionRequest
from datetime import datetime
import uuid


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine)
    session = SessionFactory()
    yield session
    session.close()


def test_create_user(db_session: Session) -> None:
    user = User(name="Test User", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    saved_user = db_session.query(User).filter_by(email="test@example.com").first()
    assert saved_user is not None
    assert saved_user.name == "Test User"
    assert saved_user.role == "guest"
    assert isinstance(saved_user.id, uuid.UUID)


def test_create_booking(db_session: Session) -> None:
    user = User(name="Booking User", email="booking@example.com")
    db_session.add(user)
    db_session.commit()

    booking = Booking(
        user_id=user.id,
        room_number="101",
        original_checkout=datetime.now()
    )
    db_session.add(booking)
    db_session.commit()

    saved_booking = db_session.query(Booking).filter_by(room_number="101").first()
    assert saved_booking is not None
    assert saved_booking.user_id == user.id
    assert saved_booking.status == "active"


def test_create_extension_request(db_session: Session) -> None:
    user = User(name="Extension User", email="extension@example.com")
    db_session.add(user)
    db_session.commit()

    booking = Booking(
        user_id=user.id,
        room_number="102",
        original_checkout=datetime.now()
    )
    db_session.add(booking)
    db_session.commit()

    extension = ExtensionRequest(
        booking_id=booking.id,
        requested_time=datetime.now()
    )
    db_session.add(extension)
    db_session.commit()

    saved_extension = db_session.query(ExtensionRequest).first()
    assert saved_extension is not None
    assert saved_extension.booking_id == booking.id
    assert saved_extension.status == "pending"
    assert saved_extension.price_quote is None
