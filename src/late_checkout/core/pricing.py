from datetime import datetime, timezone

BASE_HOURLY_RATE = 10.0


def calculate_extension_price(
    original_checkout: datetime, requested_time: datetime
) -> float:
    orig = (
        original_checkout.replace(tzinfo=timezone.utc)
        if original_checkout.tzinfo is None
        else original_checkout
    )
    req = (
        requested_time.replace(tzinfo=timezone.utc)
        if requested_time.tzinfo is None
        else requested_time
    )

    diff = req - orig
    hours = diff.total_seconds() / 3600.0
    if hours <= 0:
        return 0.0

    return round(hours * BASE_HOURLY_RATE, 2)
