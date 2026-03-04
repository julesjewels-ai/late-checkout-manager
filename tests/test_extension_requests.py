from datetime import datetime, timedelta, timezone
from uuid import uuid4, UUID
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from late_checkout.main import app
from late_checkout.models import User, Booking, ExtensionRequest

client = TestClient(app)


def test_create_extension_request(db_session: Session) -> None:
    # Setup data
    user = User(id=uuid4(), name="Test User", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    booking = Booking(
        id=uuid4(),
        user_id=user.id,
        room_number="101",
        original_checkout=datetime.now(timezone.utc)
    )
    db_session.add(booking)
    db_session.commit()

    # Test create
    requested_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    response = client.post(
        "/extension-requests",
        json={
            "booking_id": str(booking.id),
            "requested_time": requested_time
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["booking_id"] == str(booking.id)
    assert data["status"] == "pending"

    # Cleanup
    db_session.query(ExtensionRequest).filter(ExtensionRequest.id == UUID(data["id"])).delete(synchronize_session=False)
    db_session.delete(booking)
    db_session.delete(user)
    db_session.commit()


def test_create_extension_request_invalid_booking(db_session: Session) -> None:
    requested_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    response = client.post(
        "/extension-requests",
        json={
            "booking_id": str(uuid4()),
            "requested_time": requested_time
        }
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}


def test_get_extension_requests(db_session: Session) -> None:
    # Setup data
    user = User(id=uuid4(), name="Test User 2", email="test2@example.com")
    db_session.add(user)
    db_session.commit()

    booking = Booking(
        id=uuid4(),
        user_id=user.id,
        room_number="102",
        original_checkout=datetime.now(timezone.utc)
    )
    db_session.add(booking)
    db_session.commit()

    req = ExtensionRequest(
        id=uuid4(),
        booking_id=booking.id,
        requested_time=datetime.now(timezone.utc),
        status="pending"
    )
    db_session.add(req)
    db_session.commit()

    # Test get
    response = client.get(f"/extension-requests/{booking.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(req.id)

    # Cleanup
    db_session.delete(req)
    db_session.delete(booking)
    db_session.delete(user)
    db_session.commit()


def test_get_extension_requests_invalid_booking(db_session: Session) -> None:
    response = client.get(f"/extension-requests/{uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}
