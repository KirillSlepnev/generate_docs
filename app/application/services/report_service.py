from datetime import datetime, timezone
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
            raise ValueError("Report not found")

        return report.status

    async def get_download_url(self, report_id: UUID, user_id: UUID) -> str:
        report = await self._report_repo.get_by_id(report_id)

        if report is None or report.user_id != user_id:
            raise ValueError("Report not found")

        if not report.can_download:
            raise ValueError(f"Report {report_id} is not ready for download")

        assert report.file_key is not None

        return await self._file_storage.generate_presigned_url(report.file_key)

    async def user_list(self, user_id: UUID, offset: int, limit: int) -> list[Report]:
        return await self._report_repo.list_by_user(user_id, offset, limit)

    async def generate(self, report_id: UUID) -> None:
        """Запуск генерации отчета, вызывается воркером"""
        report = await self._report_repo.get_by_id(report_id)

        if report is None:
            raise ValueError("Report not found")

        template = await self._template_repo.get_by_id(report.template_id)

        if template is None:
            raise ValueError("Template not found")

        try:
            report.start_processing()
            await self._report_repo.update(report)

            if report.has_database_source:
                assert report.database_source is not None

                data = await self._data_source.fetch_data(report.database_source)
            else:
                assert report.inline_data is not None

                data = report.inline_data.data

            file_data = await self._generate_file(
                data=data,
                columns=template.columns,
                output_format=template.output_format,
                styling=template.styling,
            )

            now = datetime.now(timezone.utc)
            if template.output_format == "excel":
                ext = "xlsc"
                content_type = (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                ext = "pdf"
                content_type = "application/pdf"

            file_key = f"{report.user_id}/{now.year}/{now.month:02d}/{report.id}.{ext}"

            await self._file_storage.upload(file_data, file_key, content_type)

            report.complete(file_key)
            await self._report_repo.update(report)

        except Exception as e:
            report.fail(str(e))
            await self._report_repo.update(report)
            raise RuntimeError("Error in report generation", str(e))

    async def _generate_file(self, data, columns, output_format, styling) -> bytes:
        if output_format == "excel":
            return await self._generate_excel(data, columns, styling)
        elif output_format == "pdf":
            return await self._generate_pdf(data, columns, styling)
        else:
            raise ValueError(f"Unsupported format: {output_format}")

    async def _generate_excel(self, data, columns, styling):
        # TODO: реализовать генерацию Excel
        pass

    async def _generate_pdf(self, data, columns, styling):
        # TODO: реализовать генерацию PDF
        pass
