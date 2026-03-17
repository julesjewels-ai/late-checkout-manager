from datetime import datetime, timezone
import math


class InvalidExtensionTimeError(Exception):
    """Raised when the requested extension time is invalid."""

    pass


def calculate_extension_price(
    original_checkout: datetime,
    requested_time: datetime,
    base_rate_per_hour: float = 20.0,
) -> float:
    """
    Calculates the price quote for a late checkout extension request.

    Args:
        original_checkout: The original checkout datetime.
        requested_time: The requested extension datetime.
        base_rate_per_hour: The hourly rate for late checkout.

    Returns:
        The calculated price quote.

    Raises:
        InvalidExtensionTimeError: If the requested time is before checkout or past.
    """
    now = datetime.now(timezone.utc)

    # Ensure both datetimes are timezone-aware in UTC to prevent TypeError
    if original_checkout.tzinfo is None:
        original_checkout = original_checkout.replace(tzinfo=timezone.utc)
    if requested_time.tzinfo is None:
        requested_time = requested_time.replace(tzinfo=timezone.utc)

    if requested_time <= now:
        raise InvalidExtensionTimeError(
            "Requested extension time must be in the future."
        )

    if requested_time <= original_checkout:
        raise InvalidExtensionTimeError(
            "Requested time must be after original checkout time."
        )

    time_difference = requested_time - original_checkout
    hours_difference = time_difference.total_seconds() / 3600.0

    # Calculate price based on hours (rounding up to next whole hour)
    chargeable_hours = math.ceil(hours_difference)

    return float(chargeable_hours * base_rate_per_hour)
