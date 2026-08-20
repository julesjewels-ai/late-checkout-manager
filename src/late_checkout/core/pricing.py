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
    def __init__(
        self, base_rate_per_hour: float = 20.0, occupancy_multiplier: float = 1.0
    ):
        self.base_rate_per_hour = base_rate_per_hour
        self.occupancy_multiplier = occupancy_multiplier

    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Standardize to naive UTC to prevent mixed tz errors
        original = (
            original_checkout.astimezone(timezone.utc).replace(tzinfo=None)
            if original_checkout.tzinfo
            else original_checkout
        )
        requested = (
            requested_time.astimezone(timezone.utc).replace(tzinfo=None)
            if requested_time.tzinfo
            else requested_time
        )

        diff = requested - original
        hours = diff.total_seconds() / 3600
        if hours <= 0:
            return 0.0

        billable_hours = math.ceil(hours)
        return float(
            billable_hours * self.base_rate_per_hour * self.occupancy_multiplier
        )
