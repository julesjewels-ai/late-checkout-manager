import math
from datetime import datetime, timezone


class InvalidRequestedTimeError(Exception):
    pass


def calculate_extension_price(
    original_checkout: datetime, requested_time: datetime
) -> float:
    # Ensure both datetimes are timezone aware (default to UTC if naive)
    if original_checkout.tzinfo is None:
        original_checkout = original_checkout.replace(tzinfo=timezone.utc)
    if requested_time.tzinfo is None:
        requested_time = requested_time.replace(tzinfo=timezone.utc)

    if requested_time <= original_checkout:
        raise InvalidRequestedTimeError(
            "Requested time must be after the original checkout time"
        )

    delta = requested_time - original_checkout
    hours = math.ceil(delta.total_seconds() / 3600.0)

    return hours * 20.0
