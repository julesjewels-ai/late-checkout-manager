from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from late_checkout.models import ExtensionRequest, Booking
from late_checkout.domain.schemas import ExtensionRequestCreate


class ExtensionRequestService:
    @staticmethod
    def create_extension_request(
        db: Session, request_in: ExtensionRequestCreate
    ) -> ExtensionRequest:
        # Verify booking exists
        booking = db.query(Booking).filter(Booking.id == request_in.booking_id).first()
        if not booking:
            raise ValueError(f"Booking with ID {request_in.booking_id} not found")

        # Create extension request
        new_request = ExtensionRequest(
            booking_id=request_in.booking_id,
            requested_time=request_in.requested_time,
            status="pending"
        )
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
        return new_request

    @staticmethod
    def get_extension_request_by_id(
        db: Session, request_id: UUID
    ) -> Optional[ExtensionRequest]:
        return db.query(ExtensionRequest).filter(
            ExtensionRequest.id == request_id
        ).first()

    @staticmethod
    def get_extension_requests(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[ExtensionRequest]:
        return db.query(ExtensionRequest).offset(skip).limit(limit).all()
