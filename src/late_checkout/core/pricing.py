from datetime import datetime, timezone
from late_checkout.models import Booking


def calculate_extension_price(booking: Booking, requested_time: datetime) -> float:
    # Safely convert to UTC
    original_checkout_utc = (
        booking.original_checkout.replace(tzinfo=timezone.utc)
        if booking.original_checkout.tzinfo is None
        else booking.original_checkout.astimezone(timezone.utc)
    )
    requested_time_utc = (
        requested_time.replace(tzinfo=timezone.utc)
        if requested_time.tzinfo is None
        else requested_time.astimezone(timezone.utc)
    )

    # GRASP/SCP Mitigation: Input Validation (Score: 4)
    if requested_time_utc <= original_checkout_utc:
        raise ValueError("Requested time must be after the original checkout time.")

    diff = requested_time_utc - original_checkout_utc
    hours = diff.total_seconds() / 3600.0
    return round(hours * 20.0, 2)
