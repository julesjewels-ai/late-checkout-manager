import pytest
from datetime import datetime, timezone
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from late_checkout.main import app
from late_checkout.core.database import Base
from late_checkout.api.dependencies import get_db
from late_checkout.models import User, Booking

from sqlalchemy.pool import StaticPool

# Setup Test Database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_booking(test_db: Session) -> Booking:
    user = User(name="Test User", email="test@example.com")
    test_db.add(user)
    test_db.commit()

    now = datetime.now(timezone.utc)
    booking = Booking(
        user_id=user.id,
        room_number="101",
        original_checkout=now
    )
    test_db.add(booking)
    test_db.commit()
    test_db.refresh(booking)
    return booking


def test_create_extension_request(client: TestClient, test_booking: Booking) -> None:
    now = datetime.now(timezone.utc)
    response = client.post(
        "/extensions/",
        json={
            "booking_id": str(test_booking.id),
            "requested_time": now.isoformat()
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["booking_id"] == str(test_booking.id)
    assert data["status"] == "pending"
    assert data["price_quote"] == 20.0


def test_create_extension_request_booking_not_found(client: TestClient) -> None:
    from uuid import uuid4
    now = datetime.now(timezone.utc)
    response = client.post(
        "/extensions/",
        json={
            "booking_id": str(uuid4()),
            "requested_time": now.isoformat()
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"


def test_get_extension_requests(client: TestClient, test_booking: Booking) -> None:
    now = datetime.now(timezone.utc)
    # Create an extension first
    client.post(
        "/extensions/",
        json={
            "booking_id": str(test_booking.id),
            "requested_time": now.isoformat()
        }
    )

    response = client.get(f"/extensions/booking/{test_booking.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["booking_id"] == str(test_booking.id)
    assert data[0]["status"] == "pending"
    assert data[0]["price_quote"] == 20.0
