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
    # Set the original checkout to tomorrow to ensure it's in the future
    # relative to datetime.now(). This prevents the test from failing
    # when testing 'requested_time > original_checkout'
    original_checkout = datetime.now(timezone.utc) + timedelta(hours=24)
    booking = Booking(
        user_id=user.id,
        room_number="101",
        original_checkout=original_checkout,
        status="active",
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    return booking.id  # type: ignore


def test_create_extension_request_success(
    client: TestClient, test_booking: uuid.UUID, db_session: Session
) -> None:
    # Fetch the booking to get the exact original_checkout timestamp
    booking = db_session.query(Booking).filter(Booking.id == test_booking).first()
    assert booking is not None

    # Use + 1 hour 59 mins to test math.ceil pricing (should bill for 2 hours)
    requested_time = (
        booking.original_checkout.replace(tzinfo=timezone.utc)
        + timedelta(hours=1, minutes=59)
    ).isoformat()
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
    assert data["price_quote"] == 40.0
    assert "id" in data


def test_create_extension_request_not_found(client: TestClient) -> None:
    fake_id = str(uuid.uuid4())
    # As long as requested_time is in the future relative to datetime.now(),
    # it will hit 404 before 400
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


def test_create_extension_request_past_time(
    client: TestClient, test_booking: uuid.UUID
) -> None:
    requested_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    response = client.post(
        "/extension-requests/",
        json={
            "booking_id": str(test_booking),
            "requested_time": requested_time,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Requested time must be in the future"


def test_create_extension_request_before_checkout(
    client: TestClient, test_booking: uuid.UUID, db_session: Session
) -> None:
    booking = db_session.query(Booking).filter(Booking.id == test_booking).first()
    assert booking is not None

    requested_time = (
        booking.original_checkout.replace(tzinfo=timezone.utc) - timedelta(hours=1)
    ).isoformat()
    response = client.post(
        "/extension-requests/",
        json={
            "booking_id": str(test_booking),
            "requested_time": requested_time,
        },
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Requested time must be after the original checkout time"
    )


def test_get_extension_requests(
    client: TestClient, test_booking: uuid.UUID, db_session: Session
) -> None:
    booking = db_session.query(Booking).filter(Booking.id == test_booking).first()
    assert booking is not None

    # First create a request
    requested_time = (
        booking.original_checkout.replace(tzinfo=timezone.utc) + timedelta(hours=2)
    ).isoformat()
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
