import uuid
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from typing import Generator
from sqlalchemy.pool import StaticPool

from late_checkout.main import app
from late_checkout.core.database import Base
from late_checkout.models import User, Booking
from late_checkout.api.dependencies import get_db

# Create an in-memory SQLite database specifically for tests
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

Base.metadata.create_all(bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    # We override the session's bind to use our test engine
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def test_booking(db_session: Session) -> Booking:
    # Use a unique email per function run
    unique_email = f"api_{uuid.uuid4()}@example.com"
    user = User(name="API User", email=unique_email)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    now = datetime.now(timezone.utc)
    booking = Booking(
        user_id=user.id,
        room_number="102",
        original_checkout=now
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    return booking


def test_create_extension_request(test_booking: Booking) -> None:
    future_time = datetime.now(timezone.utc) + timedelta(hours=2)
    payload = {
        "booking_id": str(test_booking.id),
        "requested_time": future_time.isoformat()
    }
    response = client.post("/extensions/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["booking_id"] == str(test_booking.id)
    assert data["status"] == "pending"


def test_create_extension_request_past_date(test_booking: Booking) -> None:
    past_time = datetime.now(timezone.utc) - timedelta(hours=2)
    payload = {
        "booking_id": str(test_booking.id),
        "requested_time": past_time.isoformat()
    }
    response = client.post("/extensions/", json=payload)
    assert response.status_code == 422  # Pydantic validation error


def test_get_extension_request(test_booking: Booking) -> None:
    # First create one
    future_time = datetime.now(timezone.utc) + timedelta(hours=2)
    payload = {
        "booking_id": str(test_booking.id),
        "requested_time": future_time.isoformat()
    }
    create_response = client.post("/extensions/", json=payload)
    assert create_response.status_code == 201

    # Get a list of extensions
    response = client.get("/extensions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    request_id = data[0]["id"]
    # Test getting a single extension
    response_single = client.get(f"/extensions/{request_id}")
    assert response_single.status_code == 200
    assert response_single.json()["id"] == request_id
