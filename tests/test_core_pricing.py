from datetime import datetime, timezone
from late_checkout.core.pricing import calculate_extension_price


def test_calculate_extension_price_exact_hours() -> None:
    original = datetime(2023, 1, 1, 10, 0, tzinfo=timezone.utc)
    requested = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)
    price = calculate_extension_price(original, requested)
    assert price == 40.0


def test_calculate_extension_price_fractional_hours() -> None:
    original = datetime(2023, 1, 1, 10, 0, tzinfo=timezone.utc)
    requested = datetime(2023, 1, 1, 12, 15, tzinfo=timezone.utc)
    price = calculate_extension_price(original, requested)
    assert price == 60.0


def test_calculate_extension_price_zero() -> None:
    original = datetime(2023, 1, 1, 10, 0, tzinfo=timezone.utc)
    requested = datetime(2023, 1, 1, 10, 0, tzinfo=timezone.utc)
    price = calculate_extension_price(original, requested)
    assert price == 0.0


def test_calculate_extension_price_negative() -> None:
    original = datetime(2023, 1, 1, 10, 0, tzinfo=timezone.utc)
    requested = datetime(2023, 1, 1, 9, 0, tzinfo=timezone.utc)
    price = calculate_extension_price(original, requested)
    assert price == 0.0
