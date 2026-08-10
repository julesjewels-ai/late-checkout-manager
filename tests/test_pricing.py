from datetime import datetime, timezone, timedelta
from late_checkout.models import Booking
from late_checkout.core.pricing import PricingService


def test_calculate_extension_price():
    service = PricingService()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    booking = Booking(
        id="123",
        user_id="456",
        room_number="101",
        original_checkout=now,
        status="active",
    )

    requested_time = now + timedelta(hours=1, minutes=59)
    price = service.calculate_extension_price(booking, requested_time)
    assert price == 40.0
