import pytest
from datetime import datetime, timezone
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from late_checkout.main import app
from late_checkout.core.database import Base, SessionLocal, engine
from late_checkout.models import User, Booking


client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database: None) -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_create_extension_request(db_session: Session) -> None:
    # Setup test data
    user = User(name="Test User", email="test@example.com")
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

    # Run the test
    response = client.post(
        "/extensions/",
        json={
            "booking_id": str(booking.id),
            "requested_time": now.isoformat()
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["booking_id"] == str(booking.id)
    assert data["status"] == "pending"


def test_create_extension_request_booking_not_found(db_session: Session) -> None:
    import uuid
    random_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    response = client.post(
        "/extensions/",
        json={
            "booking_id": str(random_id),
            "requested_time": now.isoformat()
        }
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_extension_requests(db_session: Session) -> None:
    # Set up user and booking
    user = User(name="Test User 2", email="test2@example.com")
    db_session.add(user)
    db_session.commit()

    now = datetime.now(timezone.utc)
    booking = Booking(
        user_id=user.id,
        room_number="102",
        original_checkout=now
    )
    db_session.add(booking)
    db_session.commit()

    # Create extension request via API
    client.post(
        "/extensions/",
        json={
            "booking_id": str(booking.id),
            "requested_time": now.isoformat()
        }
    )

    # Get requests
    response = client.get(f"/extensions/booking/{booking.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["booking_id"] == str(booking.id)
