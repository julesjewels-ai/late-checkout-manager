from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from late_checkout.api.dependencies import get_db
from late_checkout.core.services import ExtensionRequestService
from late_checkout.domain.schemas import (
    ExtensionRequestCreate,
    ExtensionRequestResponse
)

router = APIRouter(
    prefix="/extensions",
    tags=["extensions"],
)


@router.post(
    "/",
    response_model=ExtensionRequestResponse,
    status_code=status.HTTP_201_CREATED
)
def create_extension_request(
    request_in: ExtensionRequestCreate,
    db: Session = Depends(get_db)
) -> ExtensionRequestResponse:
    try:
        new_req = ExtensionRequestService.create_extension_request(db, request_in)
        return ExtensionRequestResponse.model_validate(new_req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{request_id}", response_model=ExtensionRequestResponse)
def get_extension_request(
    request_id: UUID,
    db: Session = Depends(get_db)
) -> ExtensionRequestResponse:
    request = ExtensionRequestService.get_extension_request_by_id(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Extension request not found")
    return ExtensionRequestResponse.model_validate(request)


@router.get("/", response_model=List[ExtensionRequestResponse])
def get_extension_requests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[ExtensionRequestResponse]:
    requests = ExtensionRequestService.get_extension_requests(
        db, skip=skip, limit=limit
    )
    return [ExtensionRequestResponse.model_validate(r) for r in requests]
