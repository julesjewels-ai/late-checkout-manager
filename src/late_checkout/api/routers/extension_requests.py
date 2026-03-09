from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from late_checkout.api.dependencies import get_db
from late_checkout.domain.schemas import (
    ExtensionRequestCreate,
    ExtensionRequestResponse,
)
from late_checkout.services.extension_service import ExtensionService

router = APIRouter(
    prefix="/extension-requests",
    tags=["Extension Requests"],
)


def get_extension_service(db: Session = Depends(get_db)) -> ExtensionService:
    return ExtensionService(db)


@router.post(
    "/", response_model=ExtensionRequestResponse, status_code=status.HTTP_201_CREATED
)
def create_extension_request(
    request: ExtensionRequestCreate,
    service: ExtensionService = Depends(get_extension_service),
) -> ExtensionRequestResponse:
    # Additional validation logic can be added here
    new_request = service.create_extension_request(request)
    return new_request


@router.get("/{request_id}", response_model=ExtensionRequestResponse)
def get_extension_request(
    request_id: UUID,
    service: ExtensionService = Depends(get_extension_service),
) -> ExtensionRequestResponse:
    request = service.get_extension_request_by_id(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extension request not found",
        )
    return request
