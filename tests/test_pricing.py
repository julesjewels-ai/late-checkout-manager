import pytest
from datetime import datetime, timezone, timedelta

from late_checkout.core.pricing import StandardPricingService


def test_calculate_price_normal() -> None:
    service = StandardPricingService(hourly_rate=20.0)
    base_time = datetime.now(timezone.utc)
    # Use 1 hour 59 mins to avoid math.ceil exact boundaries
    req_time = base_time + timedelta(hours=1, minutes=59)
    price = service.calculate_price(base_time, req_time)
    # math.ceil(1.983) -> 2 hours -> 40.0
    assert price == 40.0


def test_calculate_price_invalid_time() -> None:
    service = StandardPricingService(hourly_rate=20.0)
    base_time = datetime.now(timezone.utc)
    # Requested time before original checkout
    req_time = base_time - timedelta(hours=1)
    with pytest.raises(
        ValueError, match="Requested time must be after original checkout time"
    ):
        service.calculate_price(base_time, req_time)
