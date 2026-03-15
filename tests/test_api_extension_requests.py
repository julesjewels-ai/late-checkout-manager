import uuid
from datetime import datetime, timezone, timedelta
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from late_checkout.main import app
from late_checkout.core.database import Base
from late_checkout.api.routers.extension_requests import get_db
from late_checkout.models import User, Booking

# Setup an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    # Create tables
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_booking(db_session: Session) -> uuid.UUID:
    # Create test user
    user = User(
        name="Test User",
        email=f"test{uuid.uuid4()}@example.com",
        role="guest",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create test booking
    booking = Booking(
        user_id=user.id,
        room_number="101",
        original_checkout=datetime.now(timezone.utc),
        status="active",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    return booking.id  # type: ignore


def test_create_extension_request_success(
    client: TestClient, test_booking: uuid.UUID
) -> None:
    requested_time = (datetime.now(timezone.utc) + timedelta(hours=2.5)).isoformat()
    response = client.post(
        "/extension-requests/",
        json={
            "booking_id": str(test_booking),
            "requested_time": requested_time,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["booking_id"] == str(test_booking)
    assert data["status"] == "pending"
    assert "id" in data
    # 2.5 hours should be rounded up to 3 hours. $20 base + (3 * $10) = $50
    assert data["price_quote"] == 50.0


def test_create_extension_request_invalid_time(
    client: TestClient, test_booking: uuid.UUID
) -> None:
    requested_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    response = client.post(
        "/extension-requests/",
        json={
            "booking_id": str(test_booking),
            "requested_time": requested_time,
        },
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"] == "Requested time must be after original checkout."
    )


def test_create_extension_request_not_found(client: TestClient) -> None:
    fake_id = str(uuid.uuid4())
    requested_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    response = client.post(
        "/extension-requests/",
        json={
            "booking_id": fake_id,
            "requested_time": requested_time,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == f"Booking {fake_id} not found"


def test_get_extension_requests(client: TestClient, test_booking: uuid.UUID) -> None:
    # First create a request
    requested_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    create_response = client.post(
        "/extension-requests/",
        json={
            "booking_id": str(test_booking),
            "requested_time": requested_time,
        },
    )
    assert create_response.status_code == 201

    # Now get requests
    response = client.get(f"/extension-requests/?booking_id={test_booking}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["booking_id"] == str(test_booking)
