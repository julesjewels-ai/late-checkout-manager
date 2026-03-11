from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from late_checkout.api.dependencies import get_db
from late_checkout.domain.models import ExtensionRequestCreate, ExtensionRequest
from late_checkout.services.extension import ExtensionService

router = APIRouter(prefix="/extension-requests", tags=["Extension Requests"])


def get_extension_service(db: Session = Depends(get_db)) -> ExtensionService:
    return ExtensionService(db)


@router.post("/", response_model=ExtensionRequest, status_code=201)
def create_extension_request(
    request_in: ExtensionRequestCreate,
    service: ExtensionService = Depends(get_extension_service),
) -> ExtensionRequest:
    return service.create_extension_request(request_in)


@router.get("/{booking_id}", response_model=List[ExtensionRequest])
def list_extension_requests(
    booking_id: UUID,
    service: ExtensionService = Depends(get_extension_service),
) -> List[ExtensionRequest]:
    return service.list_extension_requests(booking_id)
