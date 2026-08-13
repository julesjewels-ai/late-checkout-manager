import math
from datetime import datetime, timezone
from typing import Protocol


class IPricingService(Protocol):
    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float: ...


class StandardPricingService:
    def __init__(self, hourly_rate: float = 20.0):
        self.hourly_rate = hourly_rate

    def calculate_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Ensure datetimes are naive UTC for safe comparison
        orig_utc = (
            original_checkout.astimezone(timezone.utc).replace(tzinfo=None)
            if original_checkout.tzinfo
            else original_checkout
        )
        req_utc = (
            requested_time.astimezone(timezone.utc).replace(tzinfo=None)
            if requested_time.tzinfo
            else requested_time
        )

        if req_utc <= orig_utc:
            raise ValueError("Requested time must be after original checkout time")

        time_diff = req_utc - orig_utc
        hours_extended = math.ceil(time_diff.total_seconds() / 3600)
        return float(hours_extended * self.hourly_rate)
