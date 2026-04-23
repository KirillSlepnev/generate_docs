from uuid import UUID

from app.domain.models.report_template import ReportTemplate
from app.domain.models.value_objects import ColumnDefinition, StylingConfig
from app.domain.repositories.report_template import ITemplateRepository
from app.application.schemas.report_template import (
    CreateTemplateRequest,
    UpdateTemplateRequest,
)
from app.infrastructure.logging.logging import get_logger
from app.infrastructure.redis.service import CacheKeys, CacheService

logger = get_logger("template")


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

        logger.info(
            f"Template created: {template.name}",
            extra={"template_id": str(template.id), "user_id": str(user_id)},
        )

        pattern = CacheKeys.template_list_pattern(str(user_id))
        await CacheService.delete_pattern(pattern)

        logger.debug(
            "Template list cache invalidated",
            extra={"user_id": str(user_id)},
        )

        return template

    async def update(
        self, template_id: UUID, user_id: UUID, request: UpdateTemplateRequest
    ) -> ReportTemplate | None:
        template = await self._repo.get_by_id(template_id)

        if template is None or template.user_id != user_id:
            return None

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

        cache_key = CacheKeys.template(str(template_id), str(user_id))
        await CacheService.delete(cache_key)

        pattern = CacheKeys.template_list_pattern(str(user_id))
        await CacheService.delete_pattern(pattern)

        logger.debug(
            "Template list cache invalidated",
            extra={"user_id": str(user_id)},
        )

        return template

    async def delete(self, template_id: UUID, user_id: UUID) -> None:
        template = await self._repo.get_by_id(template_id)

        if template is None or template.user_id != user_id:
            raise ValueError("Template not found")

        await self._repo.delete(template_id)

        cache_key = CacheKeys.template(str(template_id), str(user_id))
        await CacheService.delete(cache_key)

        pattern = CacheKeys.template_list_pattern(str(user_id))
        await CacheService.delete_pattern(pattern)

        logger.info(
            "Template deleted",
            extra={"template_id": str(template_id), "user_id": str(user_id)},
        )

    async def get(self, template_id: UUID, user_id: UUID) -> ReportTemplate | None:
        cache_key = CacheKeys.template(str(template_id), str(user_id))

        async def fetch_template():
            template = await self._repo.get_by_id(template_id)
            if template is None or template.user_id != user_id:
                return None
            return template

        return await CacheService.get_or_set(
            key=cache_key,
            factory=fetch_template,
            expire=60,
        )

    async def list_templates(
        self, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> list[ReportTemplate]:
        cache_key = CacheKeys.template_list(str(user_id), limit, offset)

        async def fetch_list():
            return await self._repo.list_by_user(user_id, limit, offset)

        return await CacheService.get_or_set(
            key=cache_key,
            factory=fetch_list,
            expire=30,
        )
