import math
from datetime import datetime
from typing import Protocol


BASE_HOURLY_RATE = 10.0


class IPricingService(Protocol):
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        ...


class DynamicPricingService:
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Input Validation (GRASP Score: 4)
        if requested_time <= original_checkout:
            return 0.0

        duration = requested_time - original_checkout
        hours = math.ceil(duration.total_seconds() / 3600)
        return hours * BASE_HOURLY_RATE
