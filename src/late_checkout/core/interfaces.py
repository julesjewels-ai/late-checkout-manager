from abc import ABC, abstractmethod
from datetime import datetime

from late_checkout.models import Booking


class IPricingService(ABC):
    @abstractmethod
    def calculate_price(self, booking: Booking, requested_time: datetime) -> float:
        pass
