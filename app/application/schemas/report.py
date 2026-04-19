from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from datetime import datetime, date

from app.domain.models.value_objects import ReportStatus


class DatabaseSourceSchema(BaseModel):
    """Схема для источника данных из БД."""

    table: str = Field(..., description="Имя таблицы")
    fields: list[str] = Field(..., min_length=1, description="Список полей")
    date_field: str = Field(..., description="Поле с датой")
    date_from: date = Field(..., description="Начало периода")
    date_to: date = Field(..., description="Конец периода")
    filters: dict[str, object] | None = Field(
        None, description="Дополнительные фильтры"
    )


class CreateReportFromDatabaseRequest(BaseModel):
    """Запрос на создание отчета из БД."""

    template_id: str = Field(..., description="ID шаблона")
    source: DatabaseSourceSchema


class CreateReportFromInlineRequest(BaseModel):
    """Запрос на создание отчета из переданных данных."""

    template_id: str = Field(..., description="ID шаблона")
    data: list[dict[str, object]] = Field(..., min_length=1, max_length=10000)


class ReportResponse(BaseModel):
    """Ответ с данными о задаче."""

    id: UUID
    template_id: UUID
    status: ReportStatus
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("id")
    def serialize_id(self, id: UUID) -> str:
        return str(id)

    @field_serializer("template_id")
    def serialize_template_id(self, template_id: UUID) -> str:
        return str(template_id)


class ReportStatusResponse(BaseModel):
    """Ответ со статусом задачи."""

    id: UUID
    status: ReportStatus
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("id")
    def serialize_id(self, id: UUID) -> str:
        return str(id)


class DownloadUrlResponse(BaseModel):
    """Ответ со ссылкой для скачивания."""

    url: str
    expires_in: int = Field(3600, description="Время жизни ссылки в секундах")


class ReportListResponse(BaseModel):
    """Ответ со списком задач."""

    items: list[ReportResponse]
    total: int
    limit: int
    offset: int
