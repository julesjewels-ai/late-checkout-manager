import math
from datetime import datetime, timezone

BASE_HOURLY_RATE = 10.0


def _ensure_utc(dt: datetime) -> datetime:
    return (
        dt.astimezone(timezone.utc)
        if dt.tzinfo
        else dt.replace(tzinfo=timezone.utc)
    )


def calculate_price_quote(
    original_checkout: datetime, requested_time: datetime
) -> float:
    # Ensure both are UTC
    original = _ensure_utc(original_checkout)
    requested = _ensure_utc(requested_time)

    # Input Validation (GRASP Score: 4)
    if requested < original:
        raise ValueError("Requested time cannot be before original checkout time")

    time_diff = requested - original
    hours = math.ceil(time_diff.total_seconds() / 3600)

    return hours * BASE_HOURLY_RATE
