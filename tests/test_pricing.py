from datetime import datetime, timezone, timedelta

import pytest

from late_checkout.core.pricing import DynamicPricingService, InvalidRequestedTimeError


@pytest.fixture
def pricing_service() -> DynamicPricingService:
    return DynamicPricingService()


def test_calculate_price_exact_hours(pricing_service: DynamicPricingService) -> None:
    now = datetime.now(timezone.utc)
    # Original checkout in 1 hour
    original = now + timedelta(hours=1)
    # Requested time in 3 hours (2 hours extension)
    requested = now + timedelta(hours=3)

    price = pricing_service.calculate_price(original, requested)
    assert price == 40.0  # 2 hours * $20/hr


def test_calculate_price_partial_hours(pricing_service: DynamicPricingService) -> None:
    now = datetime.now(timezone.utc)
    original = now + timedelta(hours=1)
    # 2.5 hours extension, should round up to 3 hours
    requested = original + timedelta(hours=2, minutes=30)

    price = pricing_service.calculate_price(original, requested)
    assert price == 60.0  # 3 hours * $20/hr


def test_calculate_price_less_than_an_hour(
    pricing_service: DynamicPricingService,
) -> None:
    now = datetime.now(timezone.utc)
    original = now + timedelta(hours=1)
    # 15 mins extension, should round up to 1 hour
    requested = original + timedelta(minutes=15)

    price = pricing_service.calculate_price(original, requested)
    assert price == 20.0  # 1 hour * $20/hr


def test_requested_time_in_past(pricing_service: DynamicPricingService) -> None:
    now = datetime.now(timezone.utc)
    original = now - timedelta(hours=2)
    # Requested time is in the past
    requested = now - timedelta(hours=1)

    with pytest.raises(
        InvalidRequestedTimeError, match="Requested time must be in the future"
    ):
        pricing_service.calculate_price(original, requested)


def test_requested_time_before_original_checkout(
    pricing_service: DynamicPricingService,
) -> None:
    now = datetime.now(timezone.utc)
    # Original checkout is tomorrow
    original = now + timedelta(days=1)
    # Requested time is in the future, but BEFORE original checkout
    requested = now + timedelta(hours=1)

    with pytest.raises(
        InvalidRequestedTimeError,
        match="Requested time must be after original checkout",
    ):
        pricing_service.calculate_price(original, requested)


def test_naive_datetime_handling(pricing_service: DynamicPricingService) -> None:
    now = datetime.now(timezone.utc)
    # Create naive datetimes (no timezone info)
    original_naive = (now + timedelta(hours=1)).replace(tzinfo=None)
    requested_naive = (now + timedelta(hours=3)).replace(tzinfo=None)

    price = pricing_service.calculate_price(original_naive, requested_naive)
    assert price == 40.0
