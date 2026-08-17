from typing import List
from uuid import UUID

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from late_checkout.api.schemas import ExtensionRequestCreate
from late_checkout.models import Booking, ExtensionRequest
from late_checkout.core.pricing import IPricingService


class BookingNotFoundError(Exception):
    pass


class InvalidTimeError(Exception):
    pass


def create_extension_request(
    db: Session, request_data: ExtensionRequestCreate, pricing_service: IPricingService
) -> ExtensionRequest:
    # Validate booking exists
    booking = db.query(Booking).filter(Booking.id == request_data.booking_id).first()
    if not booking:
        raise BookingNotFoundError(f"Booking {request_data.booking_id} not found")

    def to_naive_utc(dt: datetime) -> datetime:
        return dt.astimezone(timezone.utc).replace(tzinfo=None) if dt.tzinfo else dt

    req_naive = to_naive_utc(request_data.requested_time)
    orig_naive = to_naive_utc(booking.original_checkout)  # type: ignore

    if req_naive <= orig_naive:
        raise InvalidTimeError("Requested time must be after original checkout time")

    price_quote = pricing_service.calculate_price(
        booking.original_checkout, request_data.requested_time  # type: ignore
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
