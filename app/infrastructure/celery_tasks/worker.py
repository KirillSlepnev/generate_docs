from uuid import UUID

from app.infrastructure.celery_tasks.celery_bus import celery_app
from app.infrastructure.database.repositories.report_repository import (
    SQLAlchemyReportRepository,
)
from app.infrastructure.database.repositories.template_repository import (
    SQLAlchemyTemplateRepository,
)
from app.infrastructure.database.session import async_session_maker
from app.infrastructure.storage.s3_storage import MinioStorage
from app.infrastructure.data_source.sql_data_source import SQLDataSource
from app.application.services.report_service import ReportService


@celery_app.task(name="app.infrastructure.celery_tasks.worker.generate_report")
def generate_report(report_id: str) -> None:
    import asyncio

    async def _run():
        async with async_session_maker() as session:
            template_repo = SQLAlchemyTemplateRepository(session)
            report_repo = SQLAlchemyReportRepository(session)
            file_storage = MinioStorage()
            data_source = SQLDataSource()

            service = ReportService(
                template_repo=template_repo,
                report_repo=report_repo,
                message_bus=None,
                file_storage=file_storage,
                data_source=data_source,
            )

            await service.generate(UUID(report_id))
            await session.commit()

    asyncio.run(_run())
