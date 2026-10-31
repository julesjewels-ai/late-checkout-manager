from datetime import timezone
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from late_checkout.api.schemas import ExtensionRequestCreate
from late_checkout.models import Booking, ExtensionRequest

BASE_HOURLY_RATE = 10.0


class BookingNotFoundError(Exception):
    pass


def create_extension_request(
    db: Session, request_data: ExtensionRequestCreate
) -> ExtensionRequest:
    # Validate booking exists
    booking = db.query(Booking).filter(Booking.id == request_data.booking_id).first()
    if not booking:
        raise BookingNotFoundError(f"Booking {request_data.booking_id} not found")

    dt1 = booking.original_checkout
    dt1 = (
        dt1.replace(tzinfo=timezone.utc)
        if dt1.tzinfo is None
        else dt1
    )

    dt2 = request_data.requested_time
    dt2 = (
        dt2.replace(tzinfo=timezone.utc)
        if dt2.tzinfo is None
        else dt2
    )

    if dt2 <= dt1:
        raise ValueError("Requested time must be after the original checkout time")

    duration_hours = (dt2 - dt1).total_seconds() / 3600.0
    price_quote = duration_hours * BASE_HOURLY_RATE

    # Create extension request
    new_request = ExtensionRequest(
        booking_id=request_data.booking_id,
        requested_time=request_data.requested_time,
        status="pending",
        price_quote=price_quote,
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request


def get_extension_requests(
    db: Session, booking_id: UUID | None = None
) -> List[ExtensionRequest]:
    query = db.query(ExtensionRequest)
    if booking_id:
        query = query.filter(ExtensionRequest.booking_id == booking_id)
    return query.all()
