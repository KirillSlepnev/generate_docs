from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.domain.models.report_template import ReportTemplate
from app.domain.models.value_objects import ColumnDefinition, StylingConfig
from app.domain.repositories.report_template import ITemplateRepository
from app.infrastructure.database.models import TemplateModel


class SQLAlchemyTemplateRepository(ITemplateRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, template: ReportTemplate) -> None:
        model = TemplateModel(
            id=template.id,
            user_id=template.user_id,
            name=template.name,
            description=template.description,
            columns=[_column_to_dict(col) for col in template.columns],
            output_format=template.output_format,
            styling=_styling_to_dict(template.styling) if template.styling else None,
            created_at=template.created_at,
            updated_at=template.updated_at,
        )

        self._session.add(model)
        await self._session.flush()

    async def get_by_id(self, template_id: UUID) -> ReportTemplate | None:
        query = select(TemplateModel).where(TemplateModel.id == template_id)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()

        return self._to_entity(model) if model is not None else None

    async def list_by_user(self, user_id, limit=100, offset=0) -> list[ReportTemplate]:
        query = (
            select(TemplateModel)
            .where(TemplateModel.user_id == user_id)
            .order_by(TemplateModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(query)
        model = result.scalars().all()
        return [self._to_entity(m) for m in model if m]

    async def update(self, template: ReportTemplate) -> None:
        query = (
            update(TemplateModel)
            .where(TemplateModel.id == template.id)
            .values(
                name=template.name,
                description=template.description,
                columns=[_column_to_dict(col) for col in template.columns],
                styling=_styling_to_dict(template.styling)
                if template.styling
                else None,
                updated_at=template.updated_at,
            )
        )
        await self._session.execute(query)

    async def delete(self, template_id: UUID) -> None:
        stmt = delete(TemplateModel).where(TemplateModel.id == template_id)
        await self._session.execute(stmt)

    def _to_entity(self, model: TemplateModel) -> ReportTemplate:
        columns = [
            ColumnDefinition(
                field=col.get("field"),
                header=col.get("header"),
                width=col.get("width"),
                format=col.get("format"),
            )
            for col in model.columns
        ]

        styling = None
        if model.styling:
            styling = StylingConfig(
                header_bg_color=model.styling.get("header_bg_color"),
                header_font_color=model.styling.get("header_font_color"),
                font_size=model.styling.get("font_size"),
                orientation=model.styling.get("orientation"),
            )

        return ReportTemplate(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            description=model.description,
            columns=columns,
            output_format=model.output_format,
            styling=styling,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


def _column_to_dict(col: ColumnDefinition) -> dict[str, Any]:
    result: dict[str, Any] = {"field": col.field, "header": col.header}
    if col.width is not None:
        result["width"] = col.width
    if col.format is not None:
        result["format"] = col.format
    return result


def _styling_to_dict(styling: StylingConfig) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if styling.header_bg_color is not None:
        result["header_bg_color"] = styling.header_bg_color
    if styling.header_font_color is not None:
        result["header_font_color"] = styling.header_font_color
    if styling.font_size is not None:
        result["font_size"] = styling.font_size
    if styling.orientation is not None:
        result["orientation"] = styling.orientation
    return result
