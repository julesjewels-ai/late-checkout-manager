import math
from datetime import datetime, timezone

from late_checkout.core.interfaces import IPricingService
from late_checkout.models import Booking

BASE_HOURLY_RATE = 10.0


class DynamicPricingService(IPricingService):
    def calculate_price(self, booking: Booking, requested_time: datetime) -> float:
        checkout = (
            booking.original_checkout.replace(tzinfo=timezone.utc)
            if booking.original_checkout.tzinfo is None
            else booking.original_checkout
        )
        req_time = (
            requested_time.replace(tzinfo=timezone.utc)
            if requested_time.tzinfo is None
            else requested_time
        )

        diff = req_time - checkout
        hours = math.ceil(diff.total_seconds() / 3600.0)
        if hours < 0:
            hours = 0

        return float(hours * BASE_HOURLY_RATE)
