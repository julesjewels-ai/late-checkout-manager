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
        orig = (
            original_checkout.replace(tzinfo=timezone.utc)
            if original_checkout.tzinfo is None
            else original_checkout.astimezone(timezone.utc)
        )
        req = (
            requested_time.replace(tzinfo=timezone.utc)
            if requested_time.tzinfo is None
            else requested_time.astimezone(timezone.utc)
        )

        if req <= orig:
            raise ValueError(
                "Requested time must be after the original checkout time."
            )

        hours = math.ceil((req - orig).total_seconds() / 3600)
        return float(hours * self.base_rate_per_hour)
