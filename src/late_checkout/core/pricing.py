from abc import ABC, abstractmethod
from datetime import datetime, timezone
import math


class IPricingService(ABC):
    @abstractmethod
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        pass


class DynamicPricingService(IPricingService):
    def __init__(self, base_rate: float, hourly_rate: float):
        self.base_rate = base_rate
        self.hourly_rate = hourly_rate

    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Ensure timezone awareness
        checkout_aware = (
            original_checkout.replace(tzinfo=timezone.utc)
            if original_checkout.tzinfo is None
            else original_checkout.astimezone(timezone.utc)
        )
        requested_aware = (
            requested_time.replace(tzinfo=timezone.utc)
            if requested_time.tzinfo is None
            else requested_time.astimezone(timezone.utc)
        )

        if requested_aware <= checkout_aware:
            raise ValueError("Requested time must be after original checkout time")

        time_diff = requested_aware - checkout_aware
        hours = time_diff.total_seconds() / 3600.0

        return self.base_rate + (math.ceil(hours) * self.hourly_rate)
