from uuid import UUID

from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.report_service import ReportService
from app.application.services.template_service import TemplateService
from app.domain.models.value_objects import OutputFormat
from app.infrastructure.celery_tasks.celery_bus import CeleryBus
from app.infrastructure.data_source.sql_data_source import SQLDataSource
from app.infrastructure.database.repositories.report_repository import (
    SQLAlchemyReportRepository,
)
from app.infrastructure.database.repositories.template_repository import (
    SQLAlchemyTemplateRepository,
)
from app.infrastructure.generators.excel_generator import ExcelGenerator
from app.infrastructure.generators.pdf_generator import PDFGenerator
from app.infrastructure.storage.s3_storage import MinioStorage


async def get_user_id(x_user_id: str = Header(...)) -> UUID:
    return UUID(x_user_id)


async def get_template_sercice(session: AsyncSession) -> TemplateService:
    repository = SQLAlchemyTemplateRepository(session)
    return TemplateService(repository)


async def get_report_service(session: AsyncSession) -> ReportService:
    template_repo = SQLAlchemyTemplateRepository(session)
    report_repo = SQLAlchemyReportRepository(session)
    message_bus = CeleryBus()
    file_storage = MinioStorage()
    data_source = SQLDataSource(session)

    generators = {
        OutputFormat.EXCEL: ExcelGenerator(),
        OutputFormat.PDF: PDFGenerator(),
    }

    return ReportService(
        template_repo=template_repo,
        report_repo=report_repo,
        message_bus=message_bus,
        file_storage=file_storage,
        data_source=data_source,
        generators=generators,
    )
