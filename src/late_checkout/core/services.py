from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from late_checkout.api.schemas import ExtensionRequestCreate
from late_checkout.models import Booking, ExtensionRequest
from late_checkout.core.pricing import DynamicPricingService


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

    if request_data.requested_time.replace(
        tzinfo=None
    ) <= booking.original_checkout.replace(tzinfo=None):
        raise InvalidRequestedTimeError(
            "Requested time must be after the original checkout time"
        )

    pricing_service = DynamicPricingService()
    price_quote = pricing_service.calculate_price(
        booking.original_checkout.replace(tzinfo=None),
        request_data.requested_time.replace(tzinfo=None),
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
