import math
from abc import ABC, abstractmethod
from datetime import datetime


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
        hours = math.ceil(duration.total_seconds() / 3600)
        return 20.0 + (10.0 * hours)
