from abc import ABC, abstractmethod
from datetime import datetime, timezone


class IPricingService(ABC):
    @abstractmethod
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        pass


class DynamicPricingService(IPricingService):
    def __init__(self, base_rate_per_hour: float):
        self.base_rate_per_hour = base_rate_per_hour

    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Safe timezone handling
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

        # Input Validation (GRASP Score: 4)
        if req <= orig:
            raise ValueError("Requested time must be after original checkout")

        time_difference = req - orig
        hours = time_difference.total_seconds() / 3600.0

        # Charge proportionally
        return round(self.base_rate_per_hour * hours, 2)
