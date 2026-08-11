from datetime import datetime, timezone
import math


def calculate_price(original_checkout: datetime, requested_time: datetime) -> float:
    # Ensure both are offset-aware for comparison (convert naive to UTC if necessary)
    if original_checkout.tzinfo is None:
        original_checkout = original_checkout.replace(tzinfo=timezone.utc)
    if requested_time.tzinfo is None:
        requested_time = requested_time.replace(tzinfo=timezone.utc)

    if requested_time <= original_checkout:
        raise ValueError("Requested time must be after the original checkout time.")

    delta = requested_time - original_checkout
    hours_difference = math.ceil(delta.total_seconds() / 3600)

    base_fee = 20.0
    hourly_rate = 10.0

    return base_fee + (hours_difference * hourly_rate)
