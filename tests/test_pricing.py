import uuid
from datetime import datetime, timezone, timedelta

import pytest

from late_checkout.core.pricing import DynamicPricingService
from late_checkout.models import Booking


def test_calculate_price_success() -> None:
    service = DynamicPricingService(hourly_rate=20.0)
    original_checkout = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
    requested_time = original_checkout + timedelta(hours=2)

    booking = Booking(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        room_number="101",
        original_checkout=original_checkout,
        status="active"
    )

    price = service.calculate_price(booking, requested_time)
    assert price == 40.0


def test_calculate_price_invalid_time() -> None:
    service = DynamicPricingService(hourly_rate=20.0)
    original_checkout = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
    requested_time = original_checkout - timedelta(hours=1)

    booking = Booking(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        room_number="101",
        original_checkout=original_checkout,
        status="active"
    )

    with pytest.raises(
        ValueError, match="Requested time must be after original checkout time"
    ):
        service.calculate_price(booking, requested_time)
