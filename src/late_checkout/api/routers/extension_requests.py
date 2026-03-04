from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from late_checkout.core.database import get_db
from late_checkout.api.schemas import ExtensionRequestCreate, ExtensionRequestResponse
from late_checkout.services.extension_request import ExtensionRequestService, IExtensionRequestService

router = APIRouter(prefix="/extension-requests", tags=["Extension Requests"])


def get_extension_request_service(db: Session = Depends(get_db)) -> IExtensionRequestService:
    return ExtensionRequestService(db)


@router.post("", response_model=ExtensionRequestResponse, status_code=201)
def create_extension_request(
    request_data: ExtensionRequestCreate,
    service: IExtensionRequestService = Depends(get_extension_request_service)
) -> ExtensionRequestResponse:
    return service.create_extension_request(request_data)


@router.get("/{booking_id}", response_model=List[ExtensionRequestResponse])
def get_extension_requests(
    booking_id: UUID,
    service: IExtensionRequestService = Depends(get_extension_request_service)
) -> List[ExtensionRequestResponse]:
    return service.get_extension_requests_by_booking(booking_id)
