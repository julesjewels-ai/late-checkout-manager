import math
from datetime import datetime, timezone


class InvalidRequestedTimeError(Exception):
    pass


def calculate_extension_price(
    original_checkout: datetime, requested_time: datetime
) -> float:
    # Ensure datetimes are offset-aware
    if original_checkout.tzinfo is None:
        original_checkout = original_checkout.replace(tzinfo=timezone.utc)
    if requested_time.tzinfo is None:
        requested_time = requested_time.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)

    # Validate requested time is in future relative to original_checkout and now
    if requested_time <= original_checkout or requested_time <= now:
        raise InvalidRequestedTimeError(
            "Requested time must be in the future relative to "
            "original checkout and current time."
        )

    # Calculate hours difference
    time_diff = requested_time - original_checkout
    hours = time_diff.total_seconds() / 3600.0

    # Round up partial hours
    billable_hours = math.ceil(hours)

    # Base rate is $20/hour
    return float(billable_hours * 20.0)
