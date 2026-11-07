BASE_HOURLY_RATE = 10.0


def calculate_extension_price(hours: float) -> float:
    return hours * BASE_HOURLY_RATE
