from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from late_checkout.core.dependencies import get_db
from late_checkout.domain.models import ExtensionRequestCreate, ExtensionRequestResponse
from late_checkout.services.extension_request_service import (
    ExtensionRequestService,
    BookingNotFoundError,
)

router = APIRouter(prefix="/extension-requests", tags=["Extension Requests"])


def get_extension_service(db: Session = Depends(get_db)) -> ExtensionRequestService:
    return ExtensionRequestService(db)


@router.post(
    "/", response_model=ExtensionRequestResponse, status_code=status.HTTP_201_CREATED
)
def create_extension_request(
    request_in: ExtensionRequestCreate,
    service: ExtensionRequestService = Depends(get_extension_service),
) -> ExtensionRequestResponse:
    try:
        return service.create_request(request_in)
    except BookingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{booking_id}", response_model=List[ExtensionRequestResponse])
def get_extension_requests(
    booking_id: UUID, service: ExtensionRequestService = Depends(get_extension_service)
) -> List[ExtensionRequestResponse]:
    return service.get_requests(booking_id)
