from datetime import datetime, timedelta, timezone
from late_checkout.core.pricing import DynamicPricingService


def test_dynamic_pricing_service_basic():
    service = DynamicPricingService(base_rate_per_hour=20.0, occupancy_multiplier=1.0)
    now = datetime.now(timezone.utc)
    # Using 1h 59m to avoid exact hour boundaries and ms rounding issues
    requested = now + timedelta(hours=1, minutes=59)
    price = service.calculate_price(now, requested)
    # ceil(1.98 hours) = 2 hours -> 2 * 20 = 40.0
    assert price == 40.0


def test_dynamic_pricing_service_negative():
    service = DynamicPricingService()
    now = datetime.now(timezone.utc)
    requested = now - timedelta(hours=1)
    price = service.calculate_price(now, requested)
    assert price == 0.0
