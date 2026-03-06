import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

from late_checkout.main import app
from late_checkout.core.dependencies import get_db
from late_checkout.core.database import Base
from late_checkout.models import User, Booking

# Use in-memory SQLite for testing to avoid interference with real DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def test_booking(test_db: Session) -> uuid.UUID:
    email = f"test_api_{uuid.uuid4()}@example.com"
    user = User(name="Test User", email=email)
    test_db.add(user)
    test_db.commit()

    booking = Booking(
        user_id=user.id, room_number="202", original_checkout=datetime.now(timezone.utc)
    )
    test_db.add(booking)
    test_db.commit()
    test_db.refresh(booking)

    return booking.id  # type: ignore


def test_create_extension_request(test_booking: uuid.UUID) -> None:
    request_data = {
        "booking_id": str(test_booking),
        "requested_time": datetime.now(timezone.utc).isoformat(),
    }

    response = client.post("/extension-requests/", json=request_data)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["booking_id"] == str(test_booking)
    assert data["status"] == "pending"


def test_create_extension_request_booking_not_found() -> None:
    fake_booking_id = str(uuid.uuid4())
    request_data = {
        "booking_id": fake_booking_id,
        "requested_time": datetime.now(timezone.utc).isoformat(),
    }

    response = client.post("/extension-requests/", json=request_data)
    assert response.status_code == 404
    assert response.json()["detail"] == f"Booking with id {fake_booking_id} not found."


def test_get_extension_requests(test_booking: uuid.UUID) -> None:
    # First, create a request to ensure there's one to get
    request_data = {
        "booking_id": str(test_booking),
        "requested_time": datetime.now(timezone.utc).isoformat(),
    }
    client.post("/extension-requests/", json=request_data)

    # Now, get the requests
    response = client.get(f"/extension-requests/{test_booking}")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["booking_id"] == str(test_booking)


def test_get_extension_requests_empty() -> None:
    fake_booking_id = str(uuid.uuid4())
    response = client.get(f"/extension-requests/{fake_booking_id}")

    assert response.status_code == 200
    assert response.json() == []
