from abc import ABC, abstractmethod
from datetime import datetime


class IPricingService(ABC):
    @abstractmethod
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        pass


class DynamicPricingService(IPricingService):
    def __init__(self, base_hourly_rate: float = 50.0):
        self.base_hourly_rate = base_hourly_rate

    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        if requested_time <= original_checkout:
            raise ValueError("Requested time must be after original checkout time")

        time_diff = requested_time - original_checkout
        hours = time_diff.total_seconds() / 3600.0
        # Dynamic pricing logic: base rate + surge based on hours requested
        # For simplicity, flat rate in this implementation
        return round(hours * self.base_hourly_rate, 2)


def get_pricing_service() -> IPricingService:
    return DynamicPricingService()
