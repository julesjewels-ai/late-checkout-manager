from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from late_checkout.models import Booking
from late_checkout.models import ExtensionRequest as ExtensionRequestORM
from late_checkout.domain.models import ExtensionRequestCreate, ExtensionRequest


class ExtensionService:
    def __init__(self, db: Session):
        self.db = db

    def create_extension_request(
        self, request_in: ExtensionRequestCreate
    ) -> ExtensionRequest:
        booking = (
            self.db.query(Booking)
            .filter(Booking.id == request_in.booking_id)
            .first()
        )
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Mocking pricing logic for now (could be an external dependency)
        price_quote = 50.0

        new_request = ExtensionRequestORM(
            booking_id=request_in.booking_id,
            requested_time=request_in.requested_time,
            price_quote=price_quote,
            status="pending"
        )
        self.db.add(new_request)
        self.db.commit()
        self.db.refresh(new_request)

        return ExtensionRequest.model_validate(new_request)

    def list_extension_requests(self, booking_id: UUID) -> List[ExtensionRequest]:
        requests = (
            self.db.query(ExtensionRequestORM)
            .filter(ExtensionRequestORM.booking_id == booking_id)
            .all()
        )
        return [ExtensionRequest.model_validate(req) for req in requests]
