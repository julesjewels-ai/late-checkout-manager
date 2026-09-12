from typing import List
from uuid import UUID

from datetime import timezone
from sqlalchemy.orm import Session

from late_checkout.api.schemas import ExtensionRequestCreate
from late_checkout.models import Booking, ExtensionRequest
from late_checkout.core.pricing import IPricingService


class BookingNotFoundError(Exception):
    pass


class InvalidRequestError(Exception):
    pass


def create_extension_request(
    db: Session, request_data: ExtensionRequestCreate, pricing_service: IPricingService
) -> ExtensionRequest:
    # Validate booking exists
    booking = db.query(Booking).filter(Booking.id == request_data.booking_id).first()
    if not booking:
        raise BookingNotFoundError(f"Booking {request_data.booking_id} not found")

    orig_naive = (
        booking.original_checkout.astimezone(timezone.utc).replace(tzinfo=None)
        if booking.original_checkout.tzinfo
        else booking.original_checkout
    )
    req_naive = (
        request_data.requested_time.astimezone(timezone.utc).replace(tzinfo=None)
        if request_data.requested_time.tzinfo
        else request_data.requested_time
    )
    if req_naive <= orig_naive:
        raise InvalidRequestError("Requested time must be after original checkout")
    price_quote = pricing_service.calculate_price(
        booking.original_checkout, request_data.requested_time
    )  # type: ignore

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
