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

    now_utc = datetime.now(timezone.utc)
    if request_data.requested_time <= now_utc:
        raise InvalidRequestedTimeError("Requested time must be in the future")

    original_checkout = booking.original_checkout
    if original_checkout.tzinfo is None:
        original_checkout = original_checkout.replace(tzinfo=timezone.utc)

    if request_data.requested_time <= original_checkout:
        raise InvalidRequestedTimeError(
            "Requested time must be after the original checkout time"
        )

    # Calculate price quote: $20/hour base rate, round up partial hours
    time_difference = request_data.requested_time - original_checkout
    hours_diff = time_difference.total_seconds() / 3600
    price_quote = math.ceil(hours_diff) * 20.0

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
