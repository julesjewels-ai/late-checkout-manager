import math
from datetime import datetime, timezone
from late_checkout.models import Booking

BASE_HOURLY_RATE = 20.0


class InvalidCheckoutTimeError(Exception):
    pass


def calculate_price_quote(booking: Booking, requested_time: datetime) -> float:
    original_checkout = booking.original_checkout.replace(tzinfo=None)
    requested_time_naive = (
        requested_time.astimezone(timezone.utc).replace(tzinfo=None)
        if requested_time.tzinfo
        else requested_time
    )

    if requested_time_naive <= original_checkout:
        raise InvalidCheckoutTimeError(
            "Requested time must be after original checkout time"
        )

    time_diff = requested_time_naive - original_checkout
    hours_extended = math.ceil(time_diff.total_seconds() / 3600)

    return float(hours_extended * BASE_HOURLY_RATE)
