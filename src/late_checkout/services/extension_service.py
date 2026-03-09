from uuid import UUID
from typing import Optional

from sqlalchemy.orm import Session

from late_checkout.models import ExtensionRequest
from late_checkout.domain.schemas import ExtensionRequestCreate


class ExtensionService:
    def __init__(self, db: Session):
        self.db = db

    def create_extension_request(self, dto: ExtensionRequestCreate) -> ExtensionRequest:
        new_request = ExtensionRequest(
            booking_id=dto.booking_id,
            requested_time=dto.requested_time,
            status="pending",
        )
        self.db.add(new_request)
        self.db.commit()
        self.db.refresh(new_request)
        return new_request

    def get_extension_request_by_id(
        self, request_id: UUID
    ) -> Optional[ExtensionRequest]:
        return (
            self.db.query(ExtensionRequest)
            .filter(ExtensionRequest.id == request_id)
            .first()
        )
