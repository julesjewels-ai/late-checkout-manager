from abc import ABC, abstractmethod
from datetime import datetime, timezone
import math


class IPricingService(ABC):
    @abstractmethod
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        pass


class InvalidTimeError(Exception):
    pass


class DynamicPricingService(IPricingService):
    def __init__(self, hourly_rate: float = 20.0):
        self.hourly_rate = hourly_rate

    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Normalize to UTC and naive datetimes for calculation
        orig_utc = original_checkout.astimezone(timezone.utc).replace(tzinfo=None)
        req_utc = requested_time.astimezone(timezone.utc).replace(tzinfo=None)

        if req_utc <= orig_utc:
            raise InvalidTimeError(
                "Requested time must be after original checkout time"
            )

        time_diff = req_utc - orig_utc
        hours = math.ceil(time_diff.total_seconds() / 3600)
        return hours * self.hourly_rate
