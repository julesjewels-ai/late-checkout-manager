import pytest
from datetime import datetime, timezone, timedelta

from late_checkout.core.services import (
    calculate_extension_price,
    InvalidRequestedTimeError,
)


def test_calculate_extension_price_valid() -> None:
    now = datetime.now(timezone.utc)
    original_checkout = now - timedelta(hours=2)
    requested_time = now + timedelta(hours=2, minutes=15)

    # Time diff is 4 hours 15 minutes, which should round up to 5 hours
    # 5 hours * $20/hour = $100.0
    price = calculate_extension_price(original_checkout, requested_time)
    assert price == 100.0


def test_calculate_extension_price_exact_hours() -> None:
    now = datetime.now(timezone.utc)
    original_checkout = now - timedelta(hours=1)
    requested_time = now + timedelta(hours=2)

    # Time diff is exactly 3 hours
    # 3 hours * $20/hour = $60.0
    price = calculate_extension_price(original_checkout, requested_time)
    assert price == 60.0


def test_calculate_extension_price_past_requested_time() -> None:
    now = datetime.now(timezone.utc)
    original_checkout = now - timedelta(hours=4)
    requested_time = now - timedelta(hours=1)

    with pytest.raises(
        InvalidRequestedTimeError, match="Requested time must be in the future"
    ):
        calculate_extension_price(original_checkout, requested_time)


def test_calculate_extension_price_before_original_checkout() -> None:
    now = datetime.now(timezone.utc)
    original_checkout = now + timedelta(hours=2)
    requested_time = now + timedelta(hours=1)

    with pytest.raises(
        InvalidRequestedTimeError,
        match="Requested time must be after the original checkout time",
    ):
        calculate_extension_price(original_checkout, requested_time)


def test_calculate_extension_price_naive_datetimes() -> None:
    # Service should ensure datetimes are offset-aware
    now = datetime.now(timezone.utc)
    original_checkout = (now - timedelta(hours=1)).replace(tzinfo=None)
    requested_time = (now + timedelta(hours=2)).replace(tzinfo=None)

    # 3 hours * $20 = $60
    price = calculate_extension_price(original_checkout, requested_time)
    assert price == 60.0
