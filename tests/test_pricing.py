from datetime import datetime, timezone
import pytest
from late_checkout.core.pricing import PricingService


def test_calculate_extension_price():
    pricing_service = PricingService()
    original_checkout = datetime(2024, 1, 1, 11, 0, tzinfo=timezone.utc)
    requested_time = datetime(2024, 1, 1, 13, 0, tzinfo=timezone.utc)
    price = pricing_service.calculate_extension_price(original_checkout, requested_time)
    assert price == pytest.approx(40.0, rel=1e-2)


def test_calculate_extension_price_negative():
    pricing_service = PricingService()
    original_checkout = datetime(2024, 1, 1, 13, 0, tzinfo=timezone.utc)
    requested_time = datetime(2024, 1, 1, 11, 0, tzinfo=timezone.utc)
    price = pricing_service.calculate_extension_price(original_checkout, requested_time)
    assert price == 0.0


def test_calculate_extension_price_rounding():
    pricing_service = PricingService()
    original_checkout = datetime(2024, 1, 1, 11, 0, tzinfo=timezone.utc)
    requested_time = datetime(2024, 1, 1, 13, 30, tzinfo=timezone.utc)
    price = pricing_service.calculate_extension_price(original_checkout, requested_time)
    # 2.5 hours rounds up to 3 hours
    assert price == pytest.approx(60.0, rel=1e-2)
