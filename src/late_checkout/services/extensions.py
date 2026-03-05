from typing import List
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from late_checkout.models import Booking as BookingModel
from late_checkout.models import ExtensionRequest as ExtensionRequestModel
from late_checkout.domain.models import ExtensionRequest


class ExtensionService:
    def __init__(self, db: Session):
        self.db = db

    def create_request(
        self, booking_id: UUID, requested_time: datetime
    ) -> ExtensionRequest:
        # Check if booking exists
        booking = self.db.query(BookingModel).filter(
            BookingModel.id == booking_id
        ).first()
        if not booking:
            raise ValueError(f"Booking with id {booking_id} not found")

        # Create the extension request
        db_request = ExtensionRequestModel(
            booking_id=booking_id,
            requested_time=requested_time,
            status="pending",
            price_quote=None  # We will calculate this later
        )
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)

        return ExtensionRequest.model_validate(
            db_request, from_attributes=True
        )

    def get_requests_for_booking(self, booking_id: UUID) -> List[ExtensionRequest]:
        requests = self.db.query(ExtensionRequestModel).filter(
            ExtensionRequestModel.booking_id == booking_id
        ).all()
        return [
            ExtensionRequest.model_validate(r, from_attributes=True)
            for r in requests
        ]
