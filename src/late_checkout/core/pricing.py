from abc import ABC, abstractmethod
from datetime import datetime, timezone
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
        # Convert to naive UTC to avoid timezone issues during math
        def to_naive_utc(dt: datetime) -> datetime:
            return dt.astimezone(timezone.utc).replace(tzinfo=None) if dt.tzinfo else dt

        orig_naive = to_naive_utc(original_checkout)
        req_naive = to_naive_utc(requested_time)

        if req_naive <= orig_naive:
            return 0.0

        time_diff = req_naive - orig_naive
        hours = math.ceil(time_diff.total_seconds() / 3600.0)

        # Base rate per hour
        base_rate = 20.0
        return float(hours * base_rate)
