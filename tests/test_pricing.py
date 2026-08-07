from datetime import datetime, timedelta, timezone
import pytest
from late_checkout.core.pricing.service import (
    calculate_extension_price,
    InvalidTimeError,
)


def test_calculate_extension_price_valid():
    orig = datetime(2023, 10, 25, 11, 0, tzinfo=timezone.utc)
    # using timedelta that avoids exact hour bounds
    req = orig + timedelta(hours=1, minutes=59)
    price = calculate_extension_price(orig, req)
    assert price == 40.0  # ceil(1.98 hours) = 2 hours * $20


def test_calculate_extension_price_past_error():
    orig = datetime.now(timezone.utc) + timedelta(hours=24)
    req = orig - timedelta(hours=1)
    with pytest.raises(
        InvalidTimeError, match="Requested time must be after original checkout."
    ):
        calculate_extension_price(orig, req)
