import math
from datetime import datetime, timezone


class InvalidTimeError(ValueError):
    pass


def calculate_extension_price(
    original_checkout: datetime, requested_time: datetime
) -> float:
    # Normalize to naive UTC datetimes to prevent timezone mismatches
    orig = (
        original_checkout.astimezone(timezone.utc).replace(tzinfo=None)
        if original_checkout.tzinfo
        else original_checkout
    )
    req = (
        requested_time.astimezone(timezone.utc).replace(tzinfo=None)
        if requested_time.tzinfo
        else requested_time
    )

    if req <= orig:
        raise InvalidTimeError("Requested time must be after original checkout.")

    diff = req - orig
    hours = math.ceil(diff.total_seconds() / 3600)
    return hours * 20.0  # $20 per hour
