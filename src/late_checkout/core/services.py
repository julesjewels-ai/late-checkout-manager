from typing import List
from datetime import timezone
from uuid import UUID

from sqlalchemy.orm import Session

from late_checkout.api.schemas import ExtensionRequestCreate
from late_checkout.core.pricing import calculate_extension_price
from late_checkout.models import Booking, ExtensionRequest


class BookingNotFoundError(Exception):
    pass


class InvalidTimeError(Exception):
    pass


def create_extension_request(
    db: Session, request_data: ExtensionRequestCreate
) -> ExtensionRequest:
    # Validate booking exists
    booking = db.query(Booking).filter(Booking.id == request_data.booking_id).first()
    if not booking:
        raise BookingNotFoundError(f"Booking {request_data.booking_id} not found")

    booking_checkout_utc = (
        booking.original_checkout.astimezone(timezone.utc)
        if booking.original_checkout.tzinfo
        else booking.original_checkout.replace(tzinfo=timezone.utc)
    )

    if request_data.requested_time <= booking_checkout_utc:
        raise InvalidTimeError("Requested time must be after original checkout time")

    time_diff = request_data.requested_time - booking_checkout_utc
    hours_extended = time_diff.total_seconds() / 3600.0
    price = calculate_extension_price(hours_extended)

    # Create extension request
    new_request = ExtensionRequest(
        booking_id=request_data.booking_id,
        requested_time=request_data.requested_time,
        status="pending",
        price_quote=price,
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
