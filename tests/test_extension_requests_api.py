from datetime import datetime, timezone
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Generator

from late_checkout.core.database import Base, SessionLocal, engine
from late_checkout.models import User, Booking, ExtensionRequest
from late_checkout.main import app


client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
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
def test_booking(db_session: Session) -> Generator[uuid.UUID, None, None]:
    unique_suffix = str(uuid.uuid4())[:8]
    user = User(
        name="API Test User",
        email=f"apitest_{unique_suffix}@example.com"
    )
    db_session.add(user)
    db_session.commit()

    now = datetime.now(timezone.utc)
    booking = Booking(
        user_id=user.id,
        room_number=f"202-{unique_suffix}",
        original_checkout=now
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    booking_id = booking.id

    yield booking_id  # type: ignore

    # Teardown
    db_session.query(ExtensionRequest).filter(
        ExtensionRequest.booking_id == booking_id
    ).delete(synchronize_session=False)
    db_session.query(Booking).filter(
        Booking.id == booking_id
    ).delete(synchronize_session=False)
    db_session.query(User).filter(
        User.id == user.id
    ).delete(synchronize_session=False)
    db_session.commit()


def test_create_extension_request(test_booking: uuid.UUID) -> None:
    now_str = datetime.now(timezone.utc).isoformat()
    response = client.post(
        "/extension-requests/",
        json={
            "booking_id": str(test_booking),
            "requested_time": now_str
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["booking_id"] == str(test_booking)
    assert data["status"] == "pending"
    assert data["price_quote"] == 50.0


def test_list_extension_requests(test_booking: uuid.UUID) -> None:
    # First create one
    now_str = datetime.now(timezone.utc).isoformat()
    create_resp = client.post(
        "/extension-requests/",
        json={
            "booking_id": str(test_booking),
            "requested_time": now_str
        }
    )
    assert create_resp.status_code == 201

    # Now list them
    response = client.get(f"/extension-requests/{test_booking}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["booking_id"] == str(test_booking)


def test_create_extension_request_invalid_booking() -> None:
    fake_booking_id = str(uuid.uuid4())
    now_str = datetime.now(timezone.utc).isoformat()
    response = client.post(
        "/extension-requests/",
        json={
            "booking_id": fake_booking_id,
            "requested_time": now_str
        }
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Booking not found"
