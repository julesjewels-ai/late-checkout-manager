from datetime import datetime, timezone
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from late_checkout.main import app
from late_checkout.core.database import Base
from late_checkout.api.dependencies import get_db
from late_checkout.models import User, Booking

# Setup Test Database for FastAPI override
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_booking(db_session: Session) -> str:
    import uuid

    unique_email = f"testapi_{uuid.uuid4()}@example.com"
    user = User(name="Test User API", email=unique_email)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    now = datetime.now(timezone.utc)
    booking = Booking(user_id=user.id, room_number="101", original_checkout=now)
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    return str(booking.id)  # type: ignore


def test_create_extension_request(test_booking: str) -> None:
    now = datetime.now(timezone.utc)
    response = client.post(
        "/extension-requests/",
        json={"booking_id": test_booking, "requested_time": now.isoformat()},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["booking_id"] == test_booking
    assert data["status"] == "pending"
    assert "id" in data


def test_get_extension_request(test_booking: str) -> None:
    now = datetime.now(timezone.utc)
    create_response = client.post(
        "/extension-requests/",
        json={"booking_id": test_booking, "requested_time": now.isoformat()},
    )
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    response = client.get(f"/extension-requests/{created_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_id
    assert data["booking_id"] == test_booking


def test_get_extension_request_not_found() -> None:
    import uuid

    random_id = str(uuid.uuid4())
    response = client.get(f"/extension-requests/{random_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Extension request not found"}
