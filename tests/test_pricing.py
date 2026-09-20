from datetime import datetime, timezone, timedelta
from late_checkout.core.pricing import DynamicPricingService


def test_pricing_service_calculates_correctly() -> None:
    service = DynamicPricingService()
    orig = datetime.now(timezone.utc).replace(tzinfo=None)

    # 1 hour extension
    req1 = orig + timedelta(hours=1)
    assert service.calculate_price(orig, req1) == 20.0

    # 2.5 hours extension (rounds to 3)
    req2 = orig + timedelta(hours=2, minutes=30)
    assert service.calculate_price(orig, req2) == 60.0

    # Negative extension
    req3 = orig - timedelta(hours=1)
    assert service.calculate_price(orig, req3) == 0.0
