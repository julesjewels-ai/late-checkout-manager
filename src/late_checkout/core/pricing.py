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
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Convert to naive UTC
        orig = (
            original_checkout.astimezone(timezone.utc).replace(tzinfo=None)
            if original_checkout.tzinfo
            else original_checkout
        )
        req = (
            requested_time.astimezone(timezone.utc).replace(tzinfo=None)
            if requested_time.tzinfo
            else requested_time
        )

        delta = req - orig
        hours = delta.total_seconds() / 3600.0
        if hours <= 0:
            return 0.0

        # Round up to nearest hour
        billable_hours = math.ceil(hours)
        base_rate = 20.0
        return float(billable_hours * base_rate)
