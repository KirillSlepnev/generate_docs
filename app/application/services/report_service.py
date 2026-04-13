from uuid import UUID

from app.domain.repositories.data_source import IDataSource
from app.domain.repositories.file_storage import IFileStorage
from app.domain.repositories.message_queue import IMessageBus
from app.domain.repositories.report import IReportRepository
from app.domain.repositories.report_template import ITemplateRepository
from app.application.schemas.report import (
    CreateReportFromDatabaseRequest,
    CreateReportFromInlineRequest,
)
from app.domain.models.report import Report
from app.domain.models.value_objects import DatabaseSource, InlineData, ReportStatus


class ReportService:
    """Сервис для управления задачами генерации отчетов"""

    def __init__(
        self,
        template_repo: ITemplateRepository,
        report_repo: IReportRepository,
        message_bus: IMessageBus,
        file_storage: IFileStorage,
        data_source: IDataSource,
    ):
        self._template_repo = template_repo
        self._report_repo = report_repo
        self._message_bus = message_bus
        self._file_storage = file_storage
        self._data_source = data_source

    async def create_from_database(
        self, user_id: UUID, request: CreateReportFromDatabaseRequest
    ) -> Report:
        template_id = UUID(request.template_id)
        template = await self._template_repo.get_by_id(template_id)

        if template is None or template.user_id != user_id:
            raise ValueError("Template not found")

        database_sourse = DatabaseSource(
            table=request.source.table,
            fields=request.source.fields,
            date_field=request.source.date_field,
            date_from=request.source.date_from,
            date_to=request.source.date_to,
            filters=request.source.filters,
        )

        report = Report.create_with_database_source(
            user_id=user_id, template_id=template_id, database_source=database_sourse
        )

        await self._report_repo.add(report)
        await self._message_bus.publish_generate_report_task(report.id)

        return report

    async def create_from_inline(
        self,
        request: CreateReportFromInlineRequest,
        user_id: UUID,
    ) -> Report:
        if len(request.data) > 1000:
            raise ValueError("Maximum 1000 rows allowed")

        if len(request.data) == 0:
            raise ValueError("Data cannot be empty")

        template_id = UUID(request.template_id)
        template = await self._template_repo.get_by_id(template_id)

        if template is None or template.user_id != user_id:
            raise ValueError("Template not found")

        inline_data = InlineData(data=request.data)

        report = Report.create_with_inline_data(
            user_id=user_id, template_id=template_id, inline_data=inline_data
        )

        await self._report_repo.add(report)
        await self._message_bus.publish_generate_report_task(report.id)

        return report

    async def get_status(self, report_id: UUID, user_id: UUID) -> ReportStatus:
        report = await self._report_repo.get_by_id(report_id)

        if report is None or report.user_id != user_id:
            raise ValueError("Template not found")

        return report.status

    async def get_download_url(self, report_id: UUID, user_id: UUID) -> str:
        report = await self._report_repo.get_by_id(report_id)

        if report is None or report.user_id != user_id:
            raise ValueError("Template not found")

        if not report.can_download:
            raise ValueError(f"Report {report_id} is not ready for download")

        assert report.file_key is not None

        return await self._file_storage.generate_presigned_url(report.file_key)
