from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.application.schemas.report import (
    CreateReportFromDatabaseRequest,
    CreateReportFromInlineRequest,
    DownloadUrlResponse,
    ReportListResponse,
    ReportResponse,
    ReportStatusResponse,
)
from app.application.services.report_service import ReportService
from app.presentation.dependecies import get_report_service, get_user_id


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/", response_model=ReportListResponse)
async def list_reports(
    limit: int = Query(100, ge=1, le=500, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    service: ReportService = Depends(get_report_service),
    user_id: UUID = Depends(get_user_id),
) -> ReportListResponse:
    reports = await service.user_list(user_id, offset, limit)

    return ReportListResponse(
        items=[ReportResponse.model_validate(r) for r in reports],
        total=len(reports),
        limit=limit,
        offset=offset,
    )


@router.post(
    "/from-database",
    response_model=ReportResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_from_database(
    request: CreateReportFromDatabaseRequest,
    user_id: UUID = Depends(get_user_id),
    service: ReportService = Depends(get_report_service),
) -> ReportResponse:
    report = await service.create_from_database(request, user_id)
    return ReportResponse.model_validate(report, from_attributes=True)


@router.post(
    "/from-inline", response_model=ReportResponse, status_code=status.HTTP_202_ACCEPTED
)
async def create_report_from_inline(
    request: CreateReportFromInlineRequest,
    service: ReportService = Depends(get_report_service),
    user_id: UUID = Depends(get_user_id),
) -> ReportResponse:
    report = await service.create_from_inline(request, user_id)
    return ReportResponse.model_validate(report, from_attributes=True)


@router.get("/{report_id}", response_model=ReportStatusResponse)
async def get_report_status(
    report_id: UUID,
    service: ReportService = Depends(get_report_service),
    user_id: UUID = Depends(get_user_id),
) -> ReportStatusResponse:
    report_status = await service.get_status(report_id, user_id)
    return ReportStatusResponse.model_validate(report_status)


@router.get("/{report_id}/download", response_model=DownloadUrlResponse)
async def get_download_url(
    report_id: UUID,
    service: ReportService = Depends(get_report_service),
    user_id: UUID = Depends(get_user_id),
) -> DownloadUrlResponse:
    url = service.get_download_url(report_id, user_id)
    return DownloadUrlResponse.model_validate(url)
