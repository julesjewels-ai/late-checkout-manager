from datetime import datetime, timezone, timedelta
from late_checkout.core.pricing import DynamicPricingService


def test_dynamic_pricing_service():
    service = DynamicPricingService()
    original_checkout = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)

    # Requested before original (expects 0.0)
    requested = original_checkout - timedelta(hours=1)
    assert service.calculate_price(original_checkout, requested) == 0.0

    # Requested exactly on time (expects 0.0)
    assert service.calculate_price(original_checkout, original_checkout) == 0.0

    # Requested 1 hour later (expects 10.0)
    requested = original_checkout + timedelta(hours=1)
    assert service.calculate_price(original_checkout, requested) == 10.0

    # Requested 2.5 hours later (expects 30.0)
    requested = original_checkout + timedelta(hours=2.5)
    assert service.calculate_price(original_checkout, requested) == 30.0
