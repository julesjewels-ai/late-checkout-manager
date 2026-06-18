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

    # Ensure datetimes are offset-aware
    requested_time = request_data.requested_time
    if requested_time.tzinfo is None:
        requested_time = requested_time.replace(tzinfo=timezone.utc)

    original_checkout = booking.original_checkout
    if original_checkout.tzinfo is None:
        original_checkout = original_checkout.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)

    # Validate requested time is in the future relative to both now
    # and original_checkout
    if requested_time <= now or requested_time <= original_checkout:
        raise InvalidRequestedTimeError(
            "Requested time must be in the future and after the "
            "original checkout time"
        )

    # Calculate hours difference (rounded up)
    hours = math.ceil((requested_time - original_checkout).total_seconds() / 3600.0)
    price_quote = hours * 20.0

    # Create extension request
    new_request = ExtensionRequest(
        booking_id=request_data.booking_id,
        requested_time=requested_time,
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
