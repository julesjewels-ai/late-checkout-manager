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


def calculate_extension_price(
    original_checkout: datetime, requested_time: datetime
) -> float:
    duration_difference = requested_time - original_checkout
    hours_difference = duration_difference.total_seconds() / 3600
    rounded_hours = math.ceil(hours_difference)
    base_rate = 20.0
    return rounded_hours * base_rate


def create_extension_request(
    db: Session, request_data: ExtensionRequestCreate
) -> ExtensionRequest:
    # Validate booking exists
    booking = db.query(Booking).filter(Booking.id == request_data.booking_id).first()
    if not booking:
        raise BookingNotFoundError(f"Booking {request_data.booking_id} not found")

    now = datetime.now(timezone.utc)
    requested_time = request_data.requested_time

    # Ensure requested_time is offset-aware
    if requested_time.tzinfo is None:
        requested_time = requested_time.replace(tzinfo=timezone.utc)

    if requested_time <= now:
        raise InvalidRequestedTimeError("Requested time must be in the future")

    original_checkout = booking.original_checkout

    # Ensure original_checkout is offset-aware
    if original_checkout.tzinfo is None:
        original_checkout = original_checkout.replace(tzinfo=timezone.utc)

    if requested_time <= original_checkout:
        raise InvalidRequestedTimeError(
            "Requested time must be after original checkout time"
        )

    # Calculate pricing
    price_quote = calculate_extension_price(original_checkout, requested_time)

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
