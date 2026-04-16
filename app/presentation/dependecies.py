from uuid import UUID

from fastapi import Depends, Header

from app.application.services.report_service import ReportService
from app.application.services.template_service import TemplateService
from app.infrastructure.database.dependecies import (
    get_report_service_impl,
    get_template_service_impl,
)


async def get_user_id(x_user_id: str = Header(...)) -> UUID:
    return UUID(x_user_id)


async def get_template_service(
    service: TemplateService = Depends(get_template_service_impl),
) -> TemplateService:
    return service


async def get_report_service(
    service: ReportService = Depends(get_report_service_impl),
) -> ReportService:
    return service
