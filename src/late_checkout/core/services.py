import math
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from late_checkout.api.schemas import ExtensionRequestCreate
from late_checkout.models import Booking, ExtensionRequest


class BookingNotFoundError(Exception):
    pass


class InvalidTimeError(Exception):
    pass


class PricingService:
    def __init__(self, hourly_rate: float):
        self.hourly_rate = hourly_rate

    def calculate_price(
        self, requested_time: datetime, original_checkout: datetime
    ) -> float:
        req_tz = (
            requested_time.replace(tzinfo=timezone.utc)
            if requested_time.tzinfo is None
            else requested_time.astimezone(timezone.utc)
        )
        orig_tz = (
            original_checkout.replace(tzinfo=timezone.utc)
            if original_checkout.tzinfo is None
            else original_checkout.astimezone(timezone.utc)
        )

        if req_tz <= orig_tz:
            raise InvalidTimeError(
                "Requested time must be after original checkout time"
            )

        diff = req_tz - orig_tz
        hours = math.ceil(diff.total_seconds() / 3600.0)
        return hours * self.hourly_rate


def create_extension_request(
    db: Session, request_data: ExtensionRequestCreate
) -> ExtensionRequest:
    # Validate booking exists
    booking = db.query(Booking).filter(Booking.id == request_data.booking_id).first()
    if not booking:
        raise BookingNotFoundError(f"Booking {request_data.booking_id} not found")

    pricing_service = PricingService(hourly_rate=1.0)
    price_quote = pricing_service.calculate_price(
        request_data.requested_time, booking.original_checkout  # type: ignore
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
