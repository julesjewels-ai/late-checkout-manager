import math
from datetime import datetime, timezone
from late_checkout.models import Booking


class PricingService:
    BASE_HOURLY_RATE = 20.0

    def calculate_extension_price(
        self, booking: Booking, requested_time: datetime
    ) -> float:
        if booking.original_checkout.tzinfo is not None:
            orig = booking.original_checkout.astimezone(timezone.utc).replace(
                tzinfo=None
            )
        else:
            orig = booking.original_checkout

        if requested_time.tzinfo is not None:
            req = requested_time.astimezone(timezone.utc).replace(tzinfo=None)
        else:
            req = requested_time

        if req <= orig:
            return 0.0

        time_diff = req - orig
        hours_extended = math.ceil(time_diff.total_seconds() / 3600.0)

        return float(hours_extended * self.BASE_HOURLY_RATE)


def get_pricing_service() -> PricingService:
    return PricingService()
