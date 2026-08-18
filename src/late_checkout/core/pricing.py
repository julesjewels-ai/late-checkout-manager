import math
from abc import ABC, abstractmethod
from datetime import datetime, timezone


class IPricingService(ABC):
    @abstractmethod
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        pass


class DynamicPricingService(IPricingService):
    def __init__(self, base_rate_per_hour: float = 20.0):
        self.base_rate_per_hour = base_rate_per_hour

    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Convert to naive UTC to safely calculate difference
        orig_naive = (
            original_checkout.astimezone(timezone.utc).replace(tzinfo=None)
            if original_checkout.tzinfo
            else original_checkout
        )
        req_naive = (
            requested_time.astimezone(timezone.utc).replace(tzinfo=None)
            if requested_time.tzinfo
            else requested_time
        )

        diff = req_naive - orig_naive
        hours = math.ceil(diff.total_seconds() / 3600)
        if hours <= 0:
            return 0.0

        return hours * self.base_rate_per_hour
