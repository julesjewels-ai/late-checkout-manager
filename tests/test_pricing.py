from datetime import datetime, timezone, timedelta
from late_checkout.core.pricing import DynamicPricingService


def test_dynamic_pricing_service() -> None:
    service = DynamicPricingService()
    orig = datetime.now(timezone.utc)
    req = orig + timedelta(hours=2, minutes=15)

    price = service.calculate_price(orig, req)
    assert price == 30.0
