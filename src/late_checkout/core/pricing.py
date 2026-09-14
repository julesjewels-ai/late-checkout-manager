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
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        if requested_time <= original_checkout:
            raise ValueError("Requested time must be after original checkout.")

        duration = requested_time - original_checkout
        duration_hours = duration.total_seconds() / 3600
        return float(math.ceil(duration_hours) * 20.0)
