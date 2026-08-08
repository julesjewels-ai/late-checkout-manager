from datetime import datetime
import math


class IPricingService:
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        raise NotImplementedError


class DynamicPricingService(IPricingService):
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        diff = requested_time - original_checkout
        hours = diff.total_seconds() / 3600.0
        return float(math.ceil(hours) * 20.0)
