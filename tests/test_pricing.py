from datetime import datetime, timedelta, timezone
import pytest
from late_checkout.core.pricing import calculate_price_quote, InvalidCheckoutTimeError
from late_checkout.models import Booking


def test_calculate_price_quote_success():
    base_time = datetime.now(timezone.utc).replace(tzinfo=None)
    booking = Booking(original_checkout=base_time)
    requested_time = base_time + timedelta(hours=1, minutes=59)
    price = calculate_price_quote(booking, requested_time)
    assert price == 40.0


def test_calculate_price_quote_invalid_time():
    base_time = datetime.now(timezone.utc).replace(tzinfo=None)
    booking = Booking(original_checkout=base_time)
    requested_time = base_time - timedelta(hours=1)
    with pytest.raises(InvalidCheckoutTimeError):
        calculate_price_quote(booking, requested_time)
