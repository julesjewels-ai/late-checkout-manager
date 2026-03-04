from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException

from late_checkout.api.schemas import ExtensionRequestCreate, ExtensionRequestResponse
from late_checkout.models import ExtensionRequest, Booking


class IExtensionRequestService(ABC):
    @abstractmethod
    def create_extension_request(self, request_data: ExtensionRequestCreate) -> ExtensionRequestResponse:
        pass

    @abstractmethod
    def get_extension_requests_by_booking(self, booking_id: UUID) -> List[ExtensionRequestResponse]:
        pass


class ExtensionRequestService(IExtensionRequestService):
    def __init__(self, db: Session):
        self.db = db

    def create_extension_request(self, request_data: ExtensionRequestCreate) -> ExtensionRequestResponse:
        booking = self.db.query(Booking).filter(
            Booking.id == request_data.booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Create the new extension request
        new_request = ExtensionRequest(
            booking_id=request_data.booking_id,
            requested_time=request_data.requested_time,
            status="pending",
        )
        self.db.add(new_request)
        self.db.commit()
        self.db.refresh(new_request)

        return ExtensionRequestResponse(
            id=new_request.id,
            booking_id=new_request.booking_id,
            requested_time=new_request.requested_time,
            status=new_request.status,
            price_quote=new_request.price_quote,
        )

    def get_extension_requests_by_booking(self, booking_id: UUID) -> List[ExtensionRequestResponse]:
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        requests = self.db.query(ExtensionRequest).filter(
            ExtensionRequest.booking_id == booking_id).all()
        return [
            ExtensionRequestResponse(
                id=req.id,
                booking_id=req.booking_id,
                requested_time=req.requested_time,
                status=req.status,
                price_quote=req.price_quote,
            )
            for req in requests
        ]
