from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from late_checkout.domain.models import ExtensionRequest as ExtensionRequestDomain
from late_checkout.domain.models import ExtensionRequestCreate
from late_checkout.models import Booking as BookingModel
from late_checkout.models import ExtensionRequest as ExtensionRequestModel


class ExtensionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_extension_request(
        self, request_data: ExtensionRequestCreate
    ) -> ExtensionRequestDomain:
        # Guard clause: ensure booking exists
        booking = (
            self.db.query(BookingModel)
            .filter(BookingModel.id == request_data.booking_id)
            .first()
        )

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Create ORM model
        db_request = ExtensionRequestModel(
            booking_id=request_data.booking_id,
            requested_time=request_data.requested_time,
        )

        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)

        # Return Pydantic domain model
        return ExtensionRequestDomain.model_validate(db_request, from_attributes=True)

    def get_extension_request(self, request_id: UUID) -> ExtensionRequestDomain:
        db_request = (
            self.db.query(ExtensionRequestModel)
            .filter(ExtensionRequestModel.id == request_id)
            .first()
        )

        if not db_request:
            raise HTTPException(status_code=404, detail="Extension request not found")

        return ExtensionRequestDomain.model_validate(db_request, from_attributes=True)
