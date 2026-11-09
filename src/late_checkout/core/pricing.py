import math
from abc import ABC, abstractmethod
from datetime import datetime, timezone

BASE_HOURLY_RATE = 10.0


class IPricingService(ABC):
    @abstractmethod
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        pass


class DynamicPricingService(IPricingService):
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        orig = (
            original_checkout.replace(tzinfo=timezone.utc)
            if original_checkout.tzinfo is None
            else original_checkout
        )
        req = (
            requested_time.replace(tzinfo=timezone.utc)
            if requested_time.tzinfo is None
            else requested_time
        )

        delta = req - orig
        hours = math.ceil(delta.total_seconds() / 3600)
        if hours < 0:
            hours = 0

        return float(hours * BASE_HOURLY_RATE)
