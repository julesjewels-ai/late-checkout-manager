from abc import ABC, abstractmethod
from datetime import datetime, timezone

from late_checkout.models import Booking


class IPricingService(ABC):
    @abstractmethod
    def calculate_price(self, booking: Booking, requested_time: datetime) -> float:
        pass


class DynamicPricingService(IPricingService):
    def __init__(self, hourly_rate: float):
        self.hourly_rate = hourly_rate

    def calculate_price(self, booking: Booking, requested_time: datetime) -> float:
        original = (
            booking.original_checkout.replace(tzinfo=timezone.utc)
            if booking.original_checkout.tzinfo is None
            else booking.original_checkout
        )

        requested = (
            requested_time.replace(tzinfo=timezone.utc)
            if requested_time.tzinfo is None
            else requested_time
        )

        if requested <= original:
            raise ValueError("Requested time must be after original checkout time")

        time_diff = requested - original
        hours_extended = time_diff.total_seconds() / 3600.0

        return float(self.hourly_rate * hours_extended)
