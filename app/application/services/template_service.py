from uuid import UUID

from app.domain.models.report_template import ReportTemplate
from app.domain.models.value_objects import ColumnDefinition, StylingConfig
from app.domain.repositories.report_template import ITemplateRepository
from app.application.schemas.report_template import (
    CreateTemplateRequest,
    UpdateTemplateRequest,
)


class TemplateService:
    """Сервис для управления шаблонами отчетов"""

    def __init__(self, repository: ITemplateRepository):
        self._repo = repository

    async def create(
        self, user_id: UUID, request: CreateTemplateRequest
    ) -> ReportTemplate:
        columns = [
            ColumnDefinition(
                field=col.field, header=col.header, width=col.width, format=col.format
            )
            for col in request.columns
        ]

        if request.styling:
            styling = StylingConfig(
                header_bg_color=request.styling.header_bg_color,
                header_font_color=request.styling.header_font_color,
                font_size=request.styling.font_size,
                orientation=request.styling.orientation,
            )
        else:
            styling = None

        template = ReportTemplate(
            user_id=user_id,
            name=request.name,
            columns=columns,
            output_format=request.output_format,
            description=request.description,
            styling=styling,
        )

        await self._repo.add(template)
        return template

    async def update(
        self, template_id: UUID, user_id: UUID, request: UpdateTemplateRequest
    ) -> ReportTemplate:
        template = await self._repo.get_by_id(template_id)

        if template is None or template.user_id != user_id:
            raise ValueError("Template not found")

        if request.columns:
            columns = [
                ColumnDefinition(
                    field=col.field,
                    header=col.header,
                    width=col.width,
                    format=col.format,
                )
                for col in request.columns
            ]
        else:
            columns = None

        if request.styling:
            styling = StylingConfig(
                header_bg_color=request.styling.header_bg_color,
                header_font_color=request.styling.header_font_color,
                font_size=request.styling.font_size,
                orientation=request.styling.orientation,
            )
        else:
            styling = None

        template.update(
            name=request.name,
            description=request.description,
            columns=columns,
            styling=styling,
        )

        await self._repo.update(template)
        return template

    async def delete(self, template_id: UUID) -> None:
        template = await self._repo.get_by_id(template_id)

        if template is None:
            raise ValueError("Template not found")

        await self._repo.delete(template_id)

    async def get(self, template_id: UUID, user_id: UUID) -> ReportTemplate:
        template = await self._repo.get_by_id(template_id)

        if template is None or template.user_id != user_id:
            raise ValueError("Template not found")

        return template

    async def list_templates(
        self, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> list[ReportTemplate]:
        return await self._repo.list_by_user(user_id, limit, offset)
