import math
from datetime import datetime, timezone


class DynamicPricingService:
    def __init__(self, base_hourly_rate: float):
        self.base_hourly_rate = base_hourly_rate

    def calculate_extension_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Standardize timezones to UTC
        safe_checkout = (
            original_checkout.replace(tzinfo=timezone.utc)
            if original_checkout.tzinfo is None
            else original_checkout.astimezone(timezone.utc)
        )
        safe_requested = (
            requested_time.replace(tzinfo=timezone.utc)
            if requested_time.tzinfo is None
            else requested_time.astimezone(timezone.utc)
        )

        if safe_requested <= safe_checkout:
            raise ValueError("Requested time must be after original checkout.")

        time_diff = safe_requested - safe_checkout
        hours = time_diff.total_seconds() / 3600.0

        return math.ceil(hours) * self.base_hourly_rate
