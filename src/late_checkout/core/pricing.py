from abc import ABC, abstractmethod
from datetime import datetime, timezone
from late_checkout.models import Booking


class InvalidRequestedTimeError(Exception):
    pass


class IPricingService(ABC):
    @abstractmethod
    def calculate_price(self, booking: Booking, requested_time: datetime) -> float:
        pass


class DynamicPricingService(IPricingService):
    def calculate_price(self, booking: Booking, requested_time: datetime) -> float:
        original = booking.original_checkout
        if original.tzinfo:
            original = original.astimezone(timezone.utc).replace(tzinfo=None)
        requested = requested_time
        if requested.tzinfo:
            requested = requested.astimezone(timezone.utc).replace(tzinfo=None)

        if requested <= original:
            raise InvalidRequestedTimeError(
                "Requested time must be after original checkout time"
            )

        time_diff = requested - original
        hours = time_diff.total_seconds() / 3600
        return round(hours * 50.0, 2)
