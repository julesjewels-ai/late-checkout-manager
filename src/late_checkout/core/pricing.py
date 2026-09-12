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
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Convert to naive UTC to avoid timezone comparison issues
        orig_naive = (
            original_checkout.astimezone(timezone.utc).replace(tzinfo=None)
            if original_checkout.tzinfo
            else original_checkout
        )
        req_naive = (
            requested_time.astimezone(timezone.utc).replace(tzinfo=None)
            if requested_time.tzinfo
            else requested_time
        )
        duration = req_naive - orig_naive
        hours = math.ceil(duration.total_seconds() / 3600.0)
        return float(max(0, hours) * 50.0)


def get_pricing_service() -> IPricingService:
    return DynamicPricingService()
