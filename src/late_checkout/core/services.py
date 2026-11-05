from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from late_checkout.api.schemas import ExtensionRequestCreate
from late_checkout.models import Booking, ExtensionRequest


class BookingNotFoundError(Exception):
    pass


def calculate_dynamic_price(
    requested_time: datetime, original_checkout: datetime
) -> float:
    # Input Validation (GRASP score: 4)
    if requested_time < original_checkout:
        raise ValueError("Requested time must be after the original checkout time.")
    diff = requested_time - original_checkout
    hours = diff.total_seconds() / 3600
    BASE_HOURLY_RATE = 10.0
    return round(hours * BASE_HOURLY_RATE, 2)


def create_extension_request(
    db: Session, request_data: ExtensionRequestCreate
) -> ExtensionRequest:
    # Validate booking exists
    booking = db.query(Booking).filter(Booking.id == request_data.booking_id).first()
    if not booking:
        raise BookingNotFoundError(f"Booking {request_data.booking_id} not found")

    req_time = (
        request_data.requested_time.replace(tzinfo=timezone.utc)
        if request_data.requested_time.tzinfo is None
        else request_data.requested_time
    )
    orig_time = (
        booking.original_checkout.replace(tzinfo=timezone.utc)
        if booking.original_checkout.tzinfo is None
        else booking.original_checkout
    )

    price_quote = calculate_dynamic_price(req_time, orig_time)

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
