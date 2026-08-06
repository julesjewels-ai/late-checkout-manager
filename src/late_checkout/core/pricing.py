import math
from datetime import datetime, timezone


def calculate_extension_price(
    original_checkout: datetime, requested_time: datetime
) -> float:
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # Ensure datetimes are timezone naive for comparison if they aren't already
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

    if req <= now:
        raise ValueError("Requested time must be in the future.")

    if req <= orig:
        raise ValueError("Requested time must be after original checkout.")

    hours = math.ceil((req - orig).total_seconds() / 3600.0)

    # Base rate of $20/hour
    return hours * 20.0
