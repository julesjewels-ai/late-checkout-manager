from datetime import datetime, timedelta
import pytest
from late_checkout.core.pricing import DynamicPricingService


def test_dynamic_pricing_calculate_price() -> None:
    service = DynamicPricingService(base_hourly_rate=50.0)
    original_checkout = datetime(2023, 1, 1, 10, 0, 0)
    requested_time = original_checkout + timedelta(hours=2)

    price = service.calculate_price(original_checkout, requested_time)
    assert price == 100.0


def test_dynamic_pricing_invalid_time() -> None:
    service = DynamicPricingService()
    original_checkout = datetime(2023, 1, 1, 10, 0, 0)
    requested_time = original_checkout - timedelta(hours=2)

    with pytest.raises(ValueError):
        service.calculate_price(original_checkout, requested_time)
