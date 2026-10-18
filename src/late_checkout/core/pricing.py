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
    def __init__(self, base_rate_per_hour: float, demand_multiplier: float):
        self.base_rate_per_hour = base_rate_per_hour
        self.demand_multiplier = demand_multiplier

    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        original = (
            original_checkout.replace(tzinfo=timezone.utc)
            if original_checkout.tzinfo is None
            else original_checkout.astimezone(timezone.utc)
        )
        requested = (
            requested_time.replace(tzinfo=timezone.utc)
            if requested_time.tzinfo is None
            else requested_time.astimezone(timezone.utc)
        )

        diff = requested - original
        hours = math.ceil(diff.total_seconds() / 3600.0)
        if hours < 0:
            return 0.0

        return hours * self.base_rate_per_hour * self.demand_multiplier
