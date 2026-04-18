from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.application.schemas.report_template import (
    CreateTemplateRequest,
    TemplateListResponse,
    TemplateResponse,
    UpdateTemplateRequest,
)
from app.application.services.template_service import TemplateService
from app.presentation.dependecies import get_template_service, get_user_id


router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    request: CreateTemplateRequest,
    service: TemplateService = Depends(get_template_service),
    user_id: UUID = Depends(get_user_id),
) -> TemplateResponse:
    template = await service.create(user_id, request)
    return TemplateResponse.model_validate(template, from_attributes=True)


@router.get("/", response_model=TemplateListResponse)
async def get_list_teplates(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: TemplateService = Depends(get_template_service),
    user_id: UUID = Depends(get_user_id),
) -> TemplateListResponse:
    templates = await service.list_templates(user_id, limit, offset)
    return TemplateListResponse(
        items=[
            TemplateResponse.model_validate(t, from_attributes=True) for t in templates
        ],
        total=len(templates),
        limit=limit,
        offset=offset,
    )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template_by_id(
    template_id: UUID,
    service: TemplateService = Depends(get_template_service),
    user_id: UUID = Depends(get_user_id),
) -> TemplateResponse:
    try:
        template = await service.get(template_id, user_id)
        return TemplateResponse.model_validate(template, from_attributes=True)
    except Exception as e:
        print(str(e))
        raise


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    request: UpdateTemplateRequest,
    template_id: UUID,
    service: TemplateService = Depends(get_template_service),
    user_id: UUID = Depends(get_user_id),
) -> TemplateResponse:
    template = await service.update(template_id, user_id, request)
    return TemplateResponse.model_validate(template, from_attributes=True)


@router.delete(
    "/{template_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
async def delete_template(
    template_id: UUID,
    service: TemplateService = Depends(get_template_service),
    user_id: UUID = Depends(get_user_id),
) -> None:
    await service.delete(template_id, user_id)
