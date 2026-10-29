from datetime import datetime, timezone, timedelta
import pytest
from late_checkout.core.pricing import (
    calculate_extension_price,
    InvalidExtensionTimeError,
)


def test_calculate_extension_price_valid() -> None:
    original = datetime.now(timezone.utc)
    requested = original + timedelta(hours=3.5)

    price = calculate_extension_price(original, requested, base_rate=20.0)
    assert price == pytest.approx(70.0, rel=1e-2)


def test_calculate_extension_price_negative_duration() -> None:
    original = datetime.now(timezone.utc)
    requested = original - timedelta(hours=1)

    with pytest.raises(
        InvalidExtensionTimeError,
        match="Requested time must be after original checkout time.",
    ):
        calculate_extension_price(original, requested)


def test_calculate_extension_price_exceeds_max_duration() -> None:
    original = datetime.now(timezone.utc)
    requested = original + timedelta(hours=25)

    with pytest.raises(
        InvalidExtensionTimeError, match="Extension cannot exceed 24 hours."
    ):
        calculate_extension_price(original, requested)
