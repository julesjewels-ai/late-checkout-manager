import math
from datetime import datetime, timezone


class InvalidRequestedTimeError(Exception):
    pass


class PricingService:
    BASE_HOURLY_RATE = 20.0

    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Ensure datetimes are offset-aware
        if original_checkout.tzinfo is None:
            original_checkout = original_checkout.replace(tzinfo=timezone.utc)
        if requested_time.tzinfo is None:
            requested_time = requested_time.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        # Validation: requested_time must be in the future
        if requested_time <= now:
            raise InvalidRequestedTimeError("Requested time must be in the future.")

        # Validation: requested_time must be strictly after the original_checkout
        if requested_time <= original_checkout:
            raise InvalidRequestedTimeError(
                "Requested time must be after the original checkout time."
            )

        # Calculate time difference
        time_diff = requested_time - original_checkout
        hours_diff = time_diff.total_seconds() / 3600.0

        # Calculate price (rounding up partial hours)
        billable_hours = math.ceil(hours_diff)
        price_quote = billable_hours * self.BASE_HOURLY_RATE

        return float(price_quote)
