from uuid import UUID
from typing import List
from sqlalchemy.orm import Session

from late_checkout.models import Booking as BookingModel
from late_checkout.models import ExtensionRequest as ExtensionRequestModel
from late_checkout.domain.models import ExtensionRequestCreate, ExtensionRequestResponse


class ExtensionService:
    def __init__(self, db: Session):
        self.db = db

    def create_extension_request(
        self, request: ExtensionRequestCreate
    ) -> ExtensionRequestResponse:
        # Check if booking exists
        booking = self.db.query(BookingModel).filter(
            BookingModel.id == request.booking_id
        ).first()
        if not booking:
            raise ValueError("Booking not found")

        # Mock dynamic pricing
        price_quote = 20.0

        db_extension = ExtensionRequestModel(
            booking_id=request.booking_id,
            requested_time=request.requested_time,
            price_quote=price_quote,
            status="pending"
        )
        self.db.add(db_extension)
        self.db.commit()
        self.db.refresh(db_extension)

        return ExtensionRequestResponse(
            id=db_extension.id,
            booking_id=db_extension.booking_id,
            requested_time=db_extension.requested_time,
            status=db_extension.status,
            price_quote=db_extension.price_quote
        )

    def get_extension_requests_by_booking(
        self, booking_id: UUID
    ) -> List[ExtensionRequestResponse]:
        db_extensions = self.db.query(ExtensionRequestModel).filter(
            ExtensionRequestModel.booking_id == booking_id
        ).all()

        return [
            ExtensionRequestResponse(
                id=ext.id,
                booking_id=ext.booking_id,
                requested_time=ext.requested_time,
                status=ext.status,
                price_quote=ext.price_quote
            )
            for ext in db_extensions
        ]
