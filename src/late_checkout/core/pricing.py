import abc
from datetime import datetime, timezone
import math


class IPricingService(abc.ABC):
    @abc.abstractmethod
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        pass


class DefaultPricingService(IPricingService):
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        orig = (
            original_checkout.astimezone(timezone.utc).replace(tzinfo=None)
            if original_checkout.tzinfo
            else original_checkout
        )
        req = (
            requested_time.astimezone(timezone.utc).replace(tzinfo=None)
            if requested_time.tzinfo
            else requested_time
        )

        diff = req - orig
        hours = math.ceil(diff.total_seconds() / 3600.0)

        if hours <= 0:
            return 0.0

        rate_per_hour = 50.0
        return float(hours * rate_per_hour)
