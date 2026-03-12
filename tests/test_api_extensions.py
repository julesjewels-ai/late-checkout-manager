from datetime import datetime, timedelta, timezone
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Generator

from late_checkout.main import app
from late_checkout.core.database import Base, SessionLocal, engine
from late_checkout.models import User, Booking


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


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_booking(db_session: Session) -> Booking:
    user = User(name="API Test User", email=f"api_{uuid.uuid4()}@example.com")
    db_session.add(user)
    db_session.commit()

    now = datetime.now(timezone.utc)
    booking = Booking(
        user_id=user.id, room_number="202", original_checkout=now + timedelta(days=1)
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    return booking


def test_create_extension_request(client: TestClient, test_booking: Booking) -> None:
    requested_time = datetime.now(timezone.utc) + timedelta(hours=2)
    payload = {
        "booking_id": str(test_booking.id),
        "requested_time": requested_time.isoformat(),
    }
    response = client.post("/extension-requests", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["booking_id"] == str(test_booking.id)
    assert data["status"] == "pending"
    assert "id" in data


def test_create_extension_request_booking_not_found(client: TestClient) -> None:
    requested_time = datetime.now(timezone.utc) + timedelta(hours=2)
    payload = {
        "booking_id": str(uuid.uuid4()),
        "requested_time": requested_time.isoformat(),
    }
    response = client.post("/extension-requests", json=payload)
    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}


def test_create_extension_request_invalid_time(
    client: TestClient, test_booking: Booking
) -> None:
    # Time in the past
    requested_time = datetime.now(timezone.utc) - timedelta(hours=2)
    payload = {
        "booking_id": str(test_booking.id),
        "requested_time": requested_time.isoformat(),
    }
    response = client.post("/extension-requests", json=payload)
    assert response.status_code == 422
    assert "requested_time must be in the future" in response.text


def test_get_extension_request(client: TestClient, test_booking: Booking) -> None:
    requested_time = datetime.now(timezone.utc) + timedelta(hours=2)
    payload = {
        "booking_id": str(test_booking.id),
        "requested_time": requested_time.isoformat(),
    }
    create_response = client.post("/extension-requests", json=payload)
    assert create_response.status_code == 200
    created_id = create_response.json()["id"]

    get_response = client.get(f"/extension-requests/{created_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == created_id
    assert data["booking_id"] == str(test_booking.id)


def test_get_extension_request_not_found(client: TestClient) -> None:
    response = client.get(f"/extension-requests/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Extension request not found"}
