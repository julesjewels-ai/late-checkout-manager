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
        base_fee = 20.0
        hourly_rate = 10.0

        # Ensure we don't have timezone offset issues by converting both to
        # naive UTC if they have tzinfo. (Though our database usually returns
        # naive datetimes, being defensive here is good)
        orig = (
            original_checkout.replace(tzinfo=None)
            if original_checkout.tzinfo
            else original_checkout
        )
        req = (
            requested_time.replace(tzinfo=None)
            if requested_time.tzinfo
            else requested_time
        )

        if req <= orig:
            return 0.0

        time_diff = req - orig
        hours = math.ceil(time_diff.total_seconds() / 3600.0)

        return base_fee + (hours * hourly_rate)
