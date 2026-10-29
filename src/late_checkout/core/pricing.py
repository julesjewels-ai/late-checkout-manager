from datetime import datetime


class InvalidExtensionTimeError(Exception):
    pass


def calculate_extension_price(
    original_checkout: datetime, requested_time: datetime, base_rate: float = 20.0
) -> float:
    # Security Control (GRASP Score 4): Input validation
    if requested_time <= original_checkout:
        raise InvalidExtensionTimeError(
            "Requested time must be after original checkout time."
        )

    duration = requested_time - original_checkout
    hours = duration.total_seconds() / 3600.0

    if hours > 24:
        raise InvalidExtensionTimeError(
            "Extension cannot exceed 24 hours."
        )

    return base_rate * hours
