from datetime import datetime
import math

# Hourly rate for extensions
HOURLY_RATE = 20.0


def calculate_extension_price(
    original_checkout: datetime, requested_time: datetime
) -> float:
    """
    Calculates the price for extending a booking.
    The price is $20 per hour (or fraction thereof) of extension.
    If requested_time is before or equal to original_checkout, price is 0.0.
    """
    if requested_time <= original_checkout:
        return 0.0

    time_diff = requested_time - original_checkout
    hours_diff = math.ceil(time_diff.total_seconds() / 3600)

    return hours_diff * HOURLY_RATE
