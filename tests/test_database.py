import uuid
from datetime import datetime
import pytest
from sqlalchemy import create_engine
from typing import Generator
from sqlalchemy.orm import sessionmaker, Session

from late_checkout.core.database import Base
from late_checkout.models import User, Booking, ExtensionRequest

# In-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_user(db: Session) -> None:
    user_id = uuid.uuid4()
    new_user = User(
        id=user_id,
        name="Test User",
        email="test@example.com",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    assert new_user.id == user_id
    assert new_user.name == "Test User"
    assert new_user.email == "test@example.com"
    assert new_user.role == "guest"


def test_create_booking(db: Session) -> None:
    user_id = uuid.uuid4()
    new_user = User(
        id=user_id,
        name="Test User",
        email="test2@example.com",
    )
    db.add(new_user)
    db.commit()

    booking_id = uuid.uuid4()
    new_booking = Booking(
        id=booking_id,
        user_id=user_id,
        room_number="102",
        original_checkout=datetime.now()
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    assert new_booking.id == booking_id
    assert new_booking.user_id == user_id
    assert new_booking.room_number == "102"
    assert new_booking.status == "active"


def test_create_extension_request(db: Session) -> None:
    user_id = uuid.uuid4()
    new_user = User(
        id=user_id,
        name="Test User",
        email="test3@example.com",
    )
    db.add(new_user)
    db.commit()

    booking_id = uuid.uuid4()
    new_booking = Booking(
        id=booking_id,
        user_id=user_id,
        room_number="103",
        original_checkout=datetime.now()
    )
    db.add(new_booking)
    db.commit()

    request_id = uuid.uuid4()
    new_request = ExtensionRequest(
        id=request_id,
        booking_id=booking_id,
        requested_time=datetime.now()
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    assert new_request.id == request_id
    assert new_request.booking_id == booking_id
    assert new_request.status == "pending"
    assert new_request.price_quote is None
