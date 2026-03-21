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

    # Timezone awareness mapping for sqlite naive datetimes
    original_checkout = booking.original_checkout
    if original_checkout.tzinfo is None:
        original_checkout = original_checkout.replace(tzinfo=timezone.utc)

    requested_time = request_data.requested_time
    if requested_time.tzinfo is None:
        requested_time = requested_time.replace(tzinfo=timezone.utc)

    # Must validate requested time is in the future
    now = datetime.now(timezone.utc)
    if requested_time <= now:
        raise InvalidRequestedTimeError("Requested time must be in the future")

    if requested_time <= original_checkout:
        raise InvalidRequestedTimeError(
            "Requested time must be after original checkout"
        )

    # Pricing logic: Dynamic pricing
    # Based on hours difference, round up to next whole hour, $20/hour
    time_diff = requested_time - original_checkout
    hours = time_diff.total_seconds() / 3600
    price_quote = math.ceil(hours) * 20.0

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
