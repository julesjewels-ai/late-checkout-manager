from datetime import datetime, timezone, timedelta
import pytest
from late_checkout.core.pricing import (
    calculate_extension_price,
    InvalidRequestedTimeError,
)


def test_calculate_price_valid_aware_datetimes() -> None:
    original = datetime.now(timezone.utc)
    requested = original + timedelta(hours=2)
    # 2 hours * $20 = $40.0
    price = calculate_extension_price(original, requested)
    assert price == 40.0


def test_calculate_price_valid_naive_datetimes() -> None:
    # Use UTC now but strip tzinfo to create a safe naive datetime
    # This prevents the test from failing when run in non-UTC timezones
    original = datetime.now(timezone.utc).replace(tzinfo=None)
    requested = original + timedelta(hours=3)
    # The pricing logic converts to aware UTC
    price = calculate_extension_price(original, requested)
    assert price == 60.0


def test_calculate_price_rounds_up() -> None:
    original = datetime.now(timezone.utc)
    # 2 hours and 15 minutes should round up to 3 hours -> $60.0
    requested = original + timedelta(hours=2, minutes=15)
    price = calculate_extension_price(original, requested)
    assert price == 60.0


def test_calculate_price_invalid_past_time() -> None:
    original = datetime.now(timezone.utc)
    # Requested time before original checkout
    requested = original - timedelta(hours=1)
    with pytest.raises(InvalidRequestedTimeError) as exc_info:
        calculate_extension_price(original, requested)
    assert "must be in the future relative to original checkout" in str(exc_info.value)


def test_calculate_price_invalid_past_time_relative_to_now() -> None:
    # Set original checkout to far past
    original = datetime.now(timezone.utc) - timedelta(hours=10)
    # Set requested time past original, but still in the past relative to NOW
    requested = datetime.now(timezone.utc) - timedelta(hours=5)
    with pytest.raises(InvalidRequestedTimeError) as exc_info:
        calculate_extension_price(original, requested)
    assert "must be in the future relative to original checkout" in str(exc_info.value)
