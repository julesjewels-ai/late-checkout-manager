from datetime import timezone
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from late_checkout.api.schemas import ExtensionRequestCreate
from late_checkout.models import Booking, ExtensionRequest
from late_checkout.core.pricing import IPricingService


class BookingNotFoundError(Exception):
    pass


def create_extension_request(
    db: Session, request_data: ExtensionRequestCreate, pricing_service: IPricingService
) -> ExtensionRequest:
    # Validate booking exists
    booking = db.query(Booking).filter(Booking.id == request_data.booking_id).first()
    if not booking:
        raise BookingNotFoundError(f"Booking {request_data.booking_id} not found")

    requested_time_utc = (
        request_data.requested_time.replace(tzinfo=timezone.utc)
        if request_data.requested_time.tzinfo is None
        else request_data.requested_time.astimezone(timezone.utc)
    )
    original_checkout_utc = (
        booking.original_checkout.replace(tzinfo=timezone.utc)
        if booking.original_checkout.tzinfo is None
        else booking.original_checkout.astimezone(timezone.utc)
    )

    if requested_time_utc <= original_checkout_utc:
        raise ValueError("Requested time must be after original checkout time")

    price_quote = pricing_service.calculate_price(
        original_checkout_utc, requested_time_utc
    )

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
