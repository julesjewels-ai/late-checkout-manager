from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from late_checkout.models import Booking as DBBooking
from late_checkout.models import ExtensionRequest as DBExtensionRequest
from late_checkout.domain.models import ExtensionRequestCreate, ExtensionRequestResponse


class BookingNotFoundError(Exception):
    """Exception raised when a booking is not found."""

    pass


class ExtensionRequestService:
    def __init__(self, db: Session):
        self.db = db

    def create_request(
        self, request_in: ExtensionRequestCreate
    ) -> ExtensionRequestResponse:
        """Creates a new extension request."""
        # Validate that the booking exists
        booking = (
            self.db.query(DBBooking)
            .filter(DBBooking.id == request_in.booking_id)
            .first()
        )
        if not booking:
            raise BookingNotFoundError(
                f"Booking with id {request_in.booking_id} not found."
            )

        # Create the request
        db_request = DBExtensionRequest(
            booking_id=request_in.booking_id, requested_time=request_in.requested_time
        )
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)

        return ExtensionRequestResponse.model_validate(db_request)

    def get_requests(self, booking_id: UUID) -> List[ExtensionRequestResponse]:
        """Gets all extension requests for a specific booking."""
        requests = (
            self.db.query(DBExtensionRequest)
            .filter(DBExtensionRequest.booking_id == booking_id)
            .all()
        )
        return [ExtensionRequestResponse.model_validate(req) for req in requests]
