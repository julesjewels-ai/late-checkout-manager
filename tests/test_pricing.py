from datetime import datetime, timezone, timedelta
from late_checkout.core.pricing import DynamicPricingService


def test_dynamic_pricing_service():
    service = DynamicPricingService()
    original_checkout = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

    # Test 2 hours extension
    requested_time = original_checkout + timedelta(hours=2)
    price = service.calculate_price(original_checkout, requested_time)
    assert price == 20.0

    # Test requested time before original checkout
    requested_time_before = original_checkout - timedelta(hours=1)
    price_before = service.calculate_price(original_checkout, requested_time_before)
    assert price_before == 0.0

    # Test requested time equal to original checkout
    price_equal = service.calculate_price(original_checkout, original_checkout)
    assert price_equal == 0.0
