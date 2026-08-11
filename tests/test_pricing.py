from datetime import datetime, timezone, timedelta
import pytest
from late_checkout.core.pricing import calculate_price


def test_calculate_price_one_hour() -> None:
    original = datetime.now(timezone.utc)
    requested = original + timedelta(hours=1)
    price = calculate_price(original, requested)
    assert price == 30.0  # 20 base + 10 * 1


def test_calculate_price_fractional_hour() -> None:
    original = datetime.now(timezone.utc)
    requested = original + timedelta(hours=1, minutes=59)
    price = calculate_price(original, requested)
    assert price == 40.0  # 20 base + 10 * 2 (ceil)


def test_calculate_price_past_time() -> None:
    original = datetime.now(timezone.utc)
    requested = original - timedelta(hours=1)
    with pytest.raises(ValueError, match="Requested time must be after"):
        calculate_price(original, requested)
