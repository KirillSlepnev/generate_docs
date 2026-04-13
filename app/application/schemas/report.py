from pydantic import BaseModel, Field
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

    id: str
    template_id: str
    status: ReportStatus
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None


class ReportStatusResponse(BaseModel):
    """Ответ со статусом задачи."""

    id: str
    status: ReportStatus
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None


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
