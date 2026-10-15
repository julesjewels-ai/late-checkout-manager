import pytest
from datetime import datetime, timezone, timedelta
from late_checkout.core.pricing import DynamicPricingService


def test_dynamic_pricing_calculation() -> None:
    service = DynamicPricingService(hourly_rate=10.0)

    original_checkout = datetime.now(timezone.utc)
    requested_time = original_checkout + timedelta(hours=2)

    price = service.calculate_price(original_checkout, requested_time)

    assert price == pytest.approx(20.0, rel=1e-2)


def test_dynamic_pricing_calculation_partial_hour() -> None:
    service = DynamicPricingService(hourly_rate=10.0)

    original_checkout = datetime.now(timezone.utc)
    requested_time = original_checkout + timedelta(hours=2, minutes=30)

    # Should round up to 3 hours
    price = service.calculate_price(original_checkout, requested_time)

    assert price == pytest.approx(30.0, rel=1e-2)
