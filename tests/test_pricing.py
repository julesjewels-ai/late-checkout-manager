import pytest
from datetime import datetime, timezone
from late_checkout.core.pricing import DynamicPricingService


def test_calculate_price_success():
    service = DynamicPricingService(base_rate_per_hour=20.0)
    original_checkout = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)
    requested_time = datetime(2023, 1, 1, 14, 0, tzinfo=timezone.utc)  # 2 hours

    price = service.calculate_price(original_checkout, requested_time)
    assert price == pytest.approx(40.0, rel=1e-2)


def test_calculate_price_fractional_hours():
    service = DynamicPricingService(base_rate_per_hour=20.0)
    original_checkout = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)
    requested_time = datetime(2023, 1, 1, 13, 30, tzinfo=timezone.utc)  # 1.5 hours

    price = service.calculate_price(original_checkout, requested_time)
    assert price == pytest.approx(30.0, rel=1e-2)


def test_calculate_price_invalid_time():
    service = DynamicPricingService(base_rate_per_hour=20.0)
    original_checkout = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)
    requested_time = datetime(2023, 1, 1, 11, 0, tzinfo=timezone.utc)  # Before checkout

    with pytest.raises(
        ValueError, match="Requested time must be after original checkout"
    ):
        service.calculate_price(original_checkout, requested_time)
