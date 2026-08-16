from datetime import datetime, timedelta, timezone
import pytest
from late_checkout.core.pricing import (
    calculate_extension_price,
    InvalidExtensionTimeError,
)


def test_calculate_extension_price_success() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    # Test with non-exact hour boundaries as per memory
    req_time = now + timedelta(hours=1, minutes=59)
    # 1 hr 59 mins -> ceil to 2 hours -> 2 * 20.0 = 40.0
    price = calculate_extension_price(now, req_time)
    assert price == 40.0


def test_calculate_extension_price_past_time() -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=24)
    req_time = now - timedelta(hours=1)
    with pytest.raises(InvalidExtensionTimeError):
        calculate_extension_price(now, req_time)
