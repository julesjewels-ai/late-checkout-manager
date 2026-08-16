import math
from datetime import datetime, timezone


class InvalidExtensionTimeError(Exception):
    pass


def calculate_extension_price(
    original_checkout: datetime, requested_time: datetime, base_rate: float = 20.0
) -> float:
    # Ensure both datetimes are naive UTC as per memory constraints
    orig_utc = (
        original_checkout.astimezone(timezone.utc).replace(tzinfo=None)
        if original_checkout.tzinfo
        else original_checkout
    )
    req_utc = (
        requested_time.astimezone(timezone.utc).replace(tzinfo=None)
        if requested_time.tzinfo
        else requested_time
    )

    if req_utc <= orig_utc:
        raise InvalidExtensionTimeError(
            "Requested time must be after original checkout time"
        )

    time_diff = req_utc - orig_utc
    hours_extended = math.ceil(time_diff.total_seconds() / 3600.0)
    return hours_extended * base_rate
