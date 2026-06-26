import math
from datetime import datetime, timezone


class InvalidRequestedTimeError(Exception):
    """Raised when the requested extension time is invalid."""
    pass


def calculate_price_quote(
    original_checkout: datetime, requested_time: datetime
) -> float:
    # Ensure datetimes are offset-aware (UTC)
    if original_checkout.tzinfo is None:
        original_checkout = original_checkout.replace(tzinfo=timezone.utc)
    if requested_time.tzinfo is None:
        requested_time = requested_time.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)

    if requested_time <= now:
        raise InvalidRequestedTimeError("Requested time must be in the future.")

    if requested_time <= original_checkout:
        raise InvalidRequestedTimeError(
            "Requested time must be after the original checkout time."
        )

    diff = requested_time - original_checkout
    hours = diff.total_seconds() / 3600

    # Round up partial hours to the next whole hour
    billed_hours = math.ceil(hours)

    base_rate = 20.0
    return billed_hours * base_rate
