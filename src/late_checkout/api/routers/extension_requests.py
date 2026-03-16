from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from late_checkout.api.schemas import ExtensionRequestCreate, ExtensionRequestResponse
from late_checkout.core.database import SessionLocal
from late_checkout.core.services import (
    create_extension_request,
    get_extension_requests,
    BookingNotFoundError,
)
from late_checkout.core.pricing import (
    DefaultPricingService,
    IPricingService,
    InvalidExtensionTimeError,
)


def get_db() -> Session:  # type: ignore
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_pricing_service() -> IPricingService:
    return DefaultPricingService()


router = APIRouter(prefix="/extension-requests", tags=["Extension Requests"])


@router.post("/", response_model=ExtensionRequestResponse, status_code=201)
def create_request(
    request_data: ExtensionRequestCreate,
    db: Session = Depends(get_db),
    pricing_service: IPricingService = Depends(get_pricing_service),
) -> ExtensionRequestResponse:
    try:
        new_request = create_extension_request(db, request_data, pricing_service)
        return ExtensionRequestResponse.model_validate(new_request)
    except BookingNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidExtensionTimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ExtensionRequestResponse])
def get_requests(
    booking_id: UUID | None = None, db: Session = Depends(get_db)
) -> List[ExtensionRequestResponse]:
    requests = get_extension_requests(db, booking_id)
    return [ExtensionRequestResponse.model_validate(req) for req in requests]
