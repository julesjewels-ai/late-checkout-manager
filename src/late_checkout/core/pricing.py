from abc import ABC, abstractmethod
from datetime import datetime
import math


class IPricingService(ABC):
    @abstractmethod
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        pass


class DynamicPricingService(IPricingService):
    def __init__(self, hourly_rate: float):
        self.hourly_rate = hourly_rate

    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Calculate time difference
        time_diff = requested_time - original_checkout

        # Calculate total hours (rounded up)
        hours_extended = math.ceil(time_diff.total_seconds() / 3600)

        # Calculate final price
        return hours_extended * self.hourly_rate
