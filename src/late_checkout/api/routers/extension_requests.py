from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from late_checkout.domain.models import ExtensionRequestCreate, ExtensionRequestResponse
from late_checkout.services.extension_service import ExtensionService
from late_checkout.api.dependencies import get_db

router = APIRouter(
    prefix="/extensions",
    tags=["extensions"]
)


@router.post("/", response_model=ExtensionRequestResponse)
def create_extension_request(
    request: ExtensionRequestCreate,
    db: Session = Depends(get_db)
) -> ExtensionRequestResponse:
    service = ExtensionService(db)
    try:
        return service.create_extension_request(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/booking/{booking_id}", response_model=List[ExtensionRequestResponse])
def get_extension_requests(
    booking_id: UUID,
    db: Session = Depends(get_db)
) -> List[ExtensionRequestResponse]:
    service = ExtensionService(db)
    return service.get_extension_requests_by_booking(booking_id)
