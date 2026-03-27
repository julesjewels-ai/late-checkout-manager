from abc import ABC, abstractmethod
from datetime import datetime, timezone
import math


class InvalidRequestedTimeError(Exception):
    pass


class IPricingService(ABC):
    @abstractmethod
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        pass


class DynamicPricingService(IPricingService):
    BASE_RATE_PER_HOUR = 20.0

    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        now = datetime.now(timezone.utc)

        # Ensure datetimes are timezone-aware
        if requested_time.tzinfo is None:
            requested_time = requested_time.replace(tzinfo=timezone.utc)
        if original_checkout.tzinfo is None:
            original_checkout = original_checkout.replace(tzinfo=timezone.utc)

        if requested_time <= now:
            raise InvalidRequestedTimeError("Requested time must be in the future")

        if requested_time <= original_checkout:
            raise InvalidRequestedTimeError(
                "Requested time must be after original checkout"
            )

        time_difference = requested_time - original_checkout
        hours = time_difference.total_seconds() / 3600.0

        # Round up partial hours
        hours_rounded_up = math.ceil(hours)

        return float(hours_rounded_up * self.BASE_RATE_PER_HOUR)
