from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from datetime import datetime

from app.domain.models.value_objects import OutputFormat


class ColumnDefinitionSchema(BaseModel):
    """Схема для описания колонки в отчете."""

    field: str = Field(..., description="Имя поля в данных")
    header: str = Field(..., description="Заголовок колонки")
    width: int | None = Field(None, description="Ширина колонки")
    format: str | None = Field(None, description="Формат отображения")

    model_config = ConfigDict(from_attributes=True)


class StylingConfigSchema(BaseModel):
    """Схема для настроек оформления."""

    header_bg_color: str | None = Field(None, description="Цвет фона заголовка")
    header_font_color: str | None = Field(None, description="Цвет шрифта заголовка")
    font_size: int | None = Field(None, description="Размер шрифта")
    orientation: str | None = Field(None, description="Ориентация страницы")

    model_config = ConfigDict(from_attributes=True)


class CreateTemplateRequest(BaseModel):
    """Запрос на создание шаблона."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    columns: list[ColumnDefinitionSchema] = Field(..., min_length=1)
    output_format: OutputFormat
    styling: StylingConfigSchema | None = None


class UpdateTemplateRequest(BaseModel):
    """Запрос на обновление шаблона."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    columns: list[ColumnDefinitionSchema] | None = Field(None, min_length=1)
    styling: StylingConfigSchema | None = None


class TemplateResponse(BaseModel):
    """Ответ с данными шаблона."""

    id: UUID
    name: str
    description: str | None
    columns: list[ColumnDefinitionSchema]
    output_format: OutputFormat
    styling: StylingConfigSchema | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("id")
    def serialize_id(self, id: UUID) -> str:
        return str(id)


class TemplateListResponse(BaseModel):
    """Ответ со списком шаблонов."""

    items: list[TemplateResponse]
    total: int
    limit: int
    offset: int
