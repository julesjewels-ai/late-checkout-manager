from datetime import datetime, timezone
import math


class PricingService:
    def __init__(self, base_rate: float = 1.0):
        self.base_rate = base_rate

    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Convert to UTC to ensure accurate comparison and calculation
        original_utc = (
            original_checkout.replace(tzinfo=timezone.utc)
            if original_checkout.tzinfo is None
            else original_checkout.astimezone(timezone.utc)
        )
        requested_utc = (
            requested_time.replace(tzinfo=timezone.utc)
            if requested_time.tzinfo is None
            else requested_time.astimezone(timezone.utc)
        )

        if requested_utc <= original_utc:
            raise ValueError(
                "Requested time must be strictly after the original checkout time."
            )

        time_difference = requested_utc - original_utc
        hours = time_difference.total_seconds() / 3600.0

        # Round up to the nearest hour for pricing
        # Using simple math.ceil
        return math.ceil(hours) * self.base_rate
