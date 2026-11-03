from abc import ABC, abstractmethod
from datetime import datetime, timezone
import math

BASE_HOURLY_RATE = 10.0


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
        # Handle timezone conversions properly to avoid offset-naive
        # and offset-aware comparison issues
        converted_checkout = (
            original_checkout.astimezone(timezone.utc)
            if original_checkout.tzinfo
            else original_checkout.replace(tzinfo=timezone.utc)
        )
        converted_time = (
            requested_time.astimezone(timezone.utc)
            if requested_time.tzinfo
            else requested_time.replace(tzinfo=timezone.utc)
        )

        # Input Validation (GRASP Score: 4)
        if converted_time <= converted_checkout:
            raise ValueError(
                "Requested time must be after the original checkout time."
            )

        time_difference = converted_time - converted_checkout

        # Input Validation (GRASP Score: 4)
        if time_difference.total_seconds() <= 0:
            raise ValueError(
                "Requested time must be after the original checkout time."
            )

        hours_extended = math.ceil(time_difference.total_seconds() / 3600)
        return hours_extended * BASE_HOURLY_RATE
