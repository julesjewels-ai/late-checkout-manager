from abc import ABC, abstractmethod
from datetime import datetime, timezone

from late_checkout.models import Booking


class InvalidExtensionTimeError(Exception):
    pass


class IPricingService(ABC):
    @abstractmethod
    def calculate_extension_price(
        self, booking: Booking, requested_time: datetime
    ) -> float:
        pass


class DefaultPricingService(IPricingService):
    HOURLY_RATE = 20.0

    def calculate_extension_price(
        self, booking: Booking, requested_time: datetime
    ) -> float:
        # Get checkout time and ensure both are aware datetimes for comparison
        checkout_time = booking.original_checkout

        # If naive, make them aware using UTC
        if checkout_time.tzinfo is None:
            checkout_time = checkout_time.replace(tzinfo=timezone.utc)

        if requested_time.tzinfo is None:
            requested_time = requested_time.replace(tzinfo=timezone.utc)

        if requested_time <= checkout_time:
            raise InvalidExtensionTimeError(
                "Requested extension time must be after the original checkout time."
            )

        time_difference = requested_time - checkout_time
        hours = time_difference.total_seconds() / 3600.0

        # Exact calculation, rounding to 2 decimals.
        price = hours * self.HOURLY_RATE
        return round(price, 2)
