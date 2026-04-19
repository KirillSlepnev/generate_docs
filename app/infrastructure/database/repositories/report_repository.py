from uuid import UUID
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.report import Report
from app.domain.models.value_objects import DatabaseSource, InlineData
from app.domain.repositories.report import IReportRepository
from app.infrastructure.database.models import ReportModel


class SQLAlchemyReportRepository(IReportRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, report: Report) -> None:
        model = ReportModel(
            id=report.id,
            user_id=report.user_id,
            template_id=report.template_id,
            status=report.status,
            database_source=_source_to_dict(report.database_source)
            if report.database_source
            else None,
            inline_data={"data": report.inline_data.data}
            if report.inline_data
            else None,
            created_at=report.created_at,
            started_at=report.started_at,
            completed_at=report.completed_at,
            file_key=report.file_key,
            error_message=report.error_message,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.flush()

    async def get_by_id(self, report_id: UUID) -> Report | None:
        query = select(ReportModel).where(ReportModel.id == report_id)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, report: Report) -> None:
        query = (
            update(ReportModel)
            .where(ReportModel.id == report.id)
            .values(
                status=report.status,
                started_at=report.started_at,
                completed_at=report.completed_at,
                file_key=report.file_key,
                error_message=report.error_message,
            )
        )
        await self._session.execute(query)
        await self._session.commit()

    async def list_by_user(
        self, user_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[Report]:
        query = (
            select(ReportModel)
            .where(ReportModel.user_id == user_id)
            .order_by(ReportModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models if m]

    def _to_entity(self, model: ReportModel) -> Report:
        database_source = None
        if model.database_source:
            database_source = DatabaseSource(
                table=model.database_source["table"],
                fields=model.database_source["fields"],
                date_field=model.database_source["date_field"],
                date_from=model.database_source["date_from"],
                date_to=model.database_source["date_to"],
                filters=model.database_source.get("filters"),
            )

        inline_data = None
        if model.inline_data:
            inline_data = InlineData(data=model.inline_data["data"])

        return Report(
            id=model.id,
            user_id=model.user_id,
            template_id=model.template_id,
            status=model.status,
            database_source=database_source,
            inline_data=inline_data,
            created_at=model.created_at,
            started_at=model.started_at,
            completed_at=model.completed_at,
            file_key=model.file_key,
            error_message=model.error_message,
        )


def _source_to_dict(source: DatabaseSource) -> dict[str, Any]:
    result: dict[str, Any] = {
        "table": source.table,
        "fields": source.fields,
        "date_field": source.date_field,
        "date_from": source.date_from.isoformat(),
        "date_to": source.date_to.isoformat(),
    }
    if source.filters is not None:
        result["filters"] = source.filters
    return result
