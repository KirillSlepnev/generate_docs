from uuid import UUID
import asyncio

from celery import shared_task

from app.domain.models.value_objects import OutputFormat
from app.infrastructure.database.repositories.report_repository import (
    SQLAlchemyReportRepository,
)
from app.infrastructure.database.repositories.template_repository import (
    SQLAlchemyTemplateRepository,
)
from app.infrastructure.database.dependecies import scoped_session
from app.infrastructure.generators.excel_generator import ExcelGenerator
from app.infrastructure.generators.pdf_generator import PDFGenerator
from app.infrastructure.logging.logging import get_logger, setup_logging
from app.infrastructure.storage.s3_storage import S3Storage
from app.infrastructure.data_source.sql_data_source import SQLDataSource
from app.application.services.report_service import ReportService


loop = asyncio.get_event_loop()

setup_logging()
logger = get_logger("celery.worker")


async def _generate_report_async(report_id: UUID) -> None:
    async with scoped_session() as session:
        template_repo = SQLAlchemyTemplateRepository(session)
        report_repo = SQLAlchemyReportRepository(session)
        file_storage = S3Storage()
        data_source = SQLDataSource(session)

        generators = {
            OutputFormat.EXCEL: ExcelGenerator(),
            OutputFormat.PDF: PDFGenerator(),
        }

        service = ReportService(
            template_repo=template_repo,
            report_repo=report_repo,
            message_bus=None,
            file_storage=file_storage,
            data_source=data_source,
            generators=generators,
        )

        await service.generate(report_id=report_id)
        await session.commit()


@shared_task(
    bind=True,
    name="app.infrastructure.celery_tasks.worker.generate_report",
    max_retries=3,
    default_retray_delay=60,
)
def generate_report_task(self, report_id: str) -> None:
    try:
        logger.info(
            "Celery task started",
            extra={"task_id": self.request.id, "report_id": report_id},
        )

        loop.run_until_complete(_generate_report_async(UUID(report_id)))
    except Exception as exc:
        logger.error(
            "Celery task failed",
            extra={
                "task_id": self.request.id,
                "report_id": report_id,
                "error": str(exc),
            },
            exc_info=True,
        )
        self.retry(exc=exc)
