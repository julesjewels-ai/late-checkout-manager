from datetime import datetime, timezone
import math


class PricingService:
    def calculate_extension_price(
        self, original_checkout: datetime, requested_time: datetime
    ) -> float:
        # Implement GRASP security control: Business Logic/State Manipulation (Score 4)
        oc = (
            original_checkout.replace(tzinfo=timezone.utc)
            if original_checkout.tzinfo is None
            else original_checkout.astimezone(timezone.utc)
        )
        rt = (
            requested_time.replace(tzinfo=timezone.utc)
            if requested_time.tzinfo is None
            else requested_time.astimezone(timezone.utc)
        )

        time_diff = rt - oc
        hours = math.ceil(time_diff.total_seconds() / 3600)
        if hours < 0:
            return 0.0

        rate_per_hour = 20.0
        return float(hours * rate_per_hour)
