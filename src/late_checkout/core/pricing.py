from abc import ABC, abstractmethod
from datetime import datetime, timezone


class IPricingService(ABC):
    @abstractmethod
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        pass


class DynamicPricingService(IPricingService):
    BASE_HOURLY_RATE = 10.0

    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        orig = (
            original_checkout.astimezone(timezone.utc)
            if original_checkout.tzinfo
            else original_checkout.replace(tzinfo=timezone.utc)
        )
        req = (
            requested_time.astimezone(timezone.utc)
            if requested_time.tzinfo
            else requested_time.replace(tzinfo=timezone.utc)
        )

        if req <= orig:
            raise ValueError("Requested time must be after the original checkout time.")

        time_diff = req - orig
        hours = time_diff.total_seconds() / 3600.0

        return hours * self.BASE_HOURLY_RATE
