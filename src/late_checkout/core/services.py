import math
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from late_checkout.api.schemas import ExtensionRequestCreate
from late_checkout.models import Booking, ExtensionRequest


class BookingNotFoundError(Exception):
    pass


class InvalidRequestedTimeError(Exception):
    pass


def create_extension_request(
    db: Session, request_data: ExtensionRequestCreate
) -> ExtensionRequest:
    # Validate booking exists
    booking = db.query(Booking).filter(Booking.id == request_data.booking_id).first()
    if not booking:
        raise BookingNotFoundError(f"Booking {request_data.booking_id} not found")

    # Time validation
    now = datetime.now(timezone.utc)

    req_time = request_data.requested_time
    if req_time.tzinfo is None:
        req_time = req_time.replace(tzinfo=timezone.utc)

    orig_checkout = booking.original_checkout
    if orig_checkout.tzinfo is None:
        orig_checkout = orig_checkout.replace(tzinfo=timezone.utc)

    if req_time <= now:
        raise InvalidRequestedTimeError("Requested time must be in the future")

    if req_time <= orig_checkout:
        raise InvalidRequestedTimeError(
            "Requested time must be after original checkout"
        )

    # Pricing logic: $20 per hour, rounded up
    time_diff = req_time - orig_checkout
    hours_diff = math.ceil(time_diff.total_seconds() / 3600.0)
    price_quote = hours_diff * 20.0

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
