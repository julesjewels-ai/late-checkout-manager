from datetime import datetime, timezone, timedelta
from late_checkout.core.pricing import calculate_extension_price


def test_calculate_extension_price() -> None:
    orig = datetime(2023, 1, 1, 10, 0, tzinfo=timezone.utc)
    req = orig + timedelta(hours=2)
    price = calculate_extension_price(orig, req)
    assert price == 20.0
