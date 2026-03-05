from typing import List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from late_checkout.domain.models import ExtensionRequest
from late_checkout.services.extensions import ExtensionService
from late_checkout.api.dependencies.database import get_db

router = APIRouter(
    prefix="/extensions",
    tags=["extensions"],
)


class ExtensionCreateDTO(BaseModel):
    booking_id: UUID
    requested_time: datetime


def get_extension_service(db: Session = Depends(get_db)) -> ExtensionService:
    return ExtensionService(db)


@router.post("/", response_model=ExtensionRequest)
def create_extension_request(
    request_data: ExtensionCreateDTO,
    service: ExtensionService = Depends(get_extension_service)
) -> ExtensionRequest:
    try:
        return service.create_request(
            booking_id=request_data.booking_id,
            requested_time=request_data.requested_time
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/booking/{booking_id}", response_model=List[ExtensionRequest])
def get_extension_requests(
    booking_id: UUID,
    service: ExtensionService = Depends(get_extension_service)
) -> List[ExtensionRequest]:
    return service.get_requests_for_booking(booking_id=booking_id)
