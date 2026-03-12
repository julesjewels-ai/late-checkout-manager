from uuid import UUID
from fastapi import APIRouter, Depends

from late_checkout.api.dependencies import get_extension_service
from late_checkout.domain.models import ExtensionRequest as ExtensionRequestDomain
from late_checkout.domain.models import ExtensionRequestCreate
from late_checkout.services.extension import ExtensionService

router = APIRouter(prefix="/extension-requests", tags=["Extension Requests"])


@router.post("", response_model=ExtensionRequestDomain)
def create_extension_request(
    request_data: ExtensionRequestCreate,
    service: ExtensionService = Depends(get_extension_service),
) -> ExtensionRequestDomain:
    return service.create_extension_request(request_data)


@router.get("/{request_id}", response_model=ExtensionRequestDomain)
def get_extension_request(
    request_id: UUID, service: ExtensionService = Depends(get_extension_service)
) -> ExtensionRequestDomain:
    return service.get_extension_request(request_id)
