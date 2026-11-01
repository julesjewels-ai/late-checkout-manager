from datetime import datetime, timezone

import pytest

from late_checkout.core.pricing import calculate_price_quote, _ensure_utc


def test_ensure_utc() -> None:
    dt = datetime(2023, 1, 1, 10, 0)
    utc_dt = _ensure_utc(dt)
    assert utc_dt.tzinfo == timezone.utc


def test_calculate_price_quote() -> None:
    original = datetime(2023, 1, 1, 10, 0, tzinfo=timezone.utc)
    requested = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)

    price = calculate_price_quote(original, requested)
    assert price == 20.0


def test_calculate_price_quote_invalid_time() -> None:
    original = datetime(2023, 1, 1, 12, 0, tzinfo=timezone.utc)
    requested = datetime(2023, 1, 1, 10, 0, tzinfo=timezone.utc)

    with pytest.raises(
        ValueError, match="Requested time cannot be before original checkout time"
    ):
        calculate_price_quote(original, requested)
