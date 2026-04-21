from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

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
# user_id = c75d2c72-c193-4f95-a9f4-9bbef906edd7
# template_id(excel) = a628349a-f929-4e42-93db-f18b0fcc19a0
# template_id(excel) все поля = 0663106f-0bbf-4f6f-a2f2-8939b95e5f12
# template_id(pdf) = c15c161a-76d1-4086-b43b-e27d0452fa5c
# template_id(pdf) все поля = 3450dd40-267c-4361-814c-038f06043fd0
# report_id = 629d067b-f8ac-4ad2-b752-6aa2bd414a3a


@router.get("/", response_model=ReportListResponse)
async def list_reports(
    limit: int = Query(100, ge=1, le=500, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    service: ReportService = Depends(get_report_service),
    user_id: UUID = Depends(get_user_id),
) -> ReportListResponse:
    reports = await service.user_list(user_id, offset, limit)
    if len(reports) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reports not found"
        )
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
    if report_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )
    return ReportStatusResponse.model_validate(report_status)


@router.get("/{report_id}/download", response_model=DownloadUrlResponse)
async def get_download_url(
    report_id: UUID,
    service: ReportService = Depends(get_report_service),
    user_id: UUID = Depends(get_user_id),
) -> DownloadUrlResponse:
    url = await service.get_download_url(report_id, user_id)
    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )
    return DownloadUrlResponse(url=url, expires_in=3600)
