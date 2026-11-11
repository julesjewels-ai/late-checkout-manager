from datetime import datetime, timezone, timedelta

from late_checkout.core.pricing_service import DynamicPricingService
from late_checkout.models import Booking


def test_dynamic_pricing_service() -> None:
    service = DynamicPricingService()
    now = datetime.now(timezone.utc)
    booking = Booking(
        original_checkout=now
    )

    # Test 2 hours
    requested_time = now + timedelta(hours=2)
    price = service.calculate_price(booking, requested_time)
    assert price == 20.0

    # Test fraction (2.5 hours)
    requested_time_frac = now + timedelta(hours=2, minutes=30)
    price_frac = service.calculate_price(booking, requested_time_frac)
    assert price_frac == 30.0

    # Test before checkout (should be 0)
    requested_time_early = now - timedelta(hours=1)
    price_early = service.calculate_price(booking, requested_time_early)
    assert price_early == 0.0
