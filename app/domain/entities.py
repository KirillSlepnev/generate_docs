from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import List

from app.domain.value_objects import (
    ColumnDefinition,
    OutputFormat,
    StylingConfig,
    ReportStatus,
    DatabaseSource,
    InlineData,
)


@dataclass
class ReportTemplate:
    """
    Сохраненная конфигурация оформления отчета

    Не содержит информации об источнике данных — только то,
    как данные должны быть отображены в итоговом файле

    Args:
        user_id: id пользователя, создавшего шаблон
        name: название шаблона
        columns: поля, которые будут использованы в отчете,
                объекты ColumnDefinition
        output_format: выбор формата отчета (OutputFormat)
        id: id шаблона
        created_at: время создания
        updated_at: время обновления
        description: дополнительное описание шаблона
        styling: оформление по StylingConfig
    """

    user_id: UUID
    name: str
    columns: List[ColumnDefinition]
    output_format: OutputFormat
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    description: str | None = None
    styling: StylingConfig | None = None

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        columns: List[ColumnDefinition] | None = None,
        styling: StylingConfig | None = None,
    ) -> None:
        """
        Обновляет изменяемые поля шаблона
        Автоматически обновляет updated_at
        """
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if columns is not None:
            self.columns = columns
        if styling is not None:
            self.styling = styling
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class Report:
    """
    Конкретная задача на генерацию отчета

    Всегда создается на основе существующего шаблона
    Содержит либо database_source, либо inline_data

    Args:
        id: id задачи на генерацию
        user_id: id пользователя, запустившего генерацию
        template_id: id шаблона отчета
        status: объекты ReportStatus (PENDING -> PROCESSING -> COMPLETED/FAILED)
        created_at: время создания задачи
        database_source: объект DatabaseSource - источник бд
        inline_data: объект InlineData - источник "сырые данные"
                    database_source и inline_data не могут быть заполнены одновременно
        started_at: время начала генерации отчета
        completed_at: время завершения генерации
        file_key: ключ файла в S3
        error_message: сообщение об ошибке
    """

    id: UUID
    user_id: UUID
    template_id: UUID
    status: ReportStatus
    created_at: datetime
    database_source: DatabaseSource | None = None
    inline_data: InlineData | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    file_key: str | None = None
    error_message: str | None = None

    @classmethod
    def create_with_database_source(
        cls,
        user_id: UUID,
        template_id: UUID,
        database_source: DatabaseSource,
    ) -> "Report":
        return cls(
            id=uuid4(),
            user_id=user_id,
            template_id=template_id,
            database_source=database_source,
            status=ReportStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )

    @classmethod
    def create_with_inline_data(
        cls,
        user_id: UUID,
        template_id: UUID,
        inline_data: InlineData,
    ) -> "Report":
        return cls(
            id=uuid4(),
            user_id=user_id,
            template_id=template_id,
            inline_data=inline_data,
            status=ReportStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )

    def start_processing(self) -> None:
        """
        Отмечает, что воркер начал генерацию
        Может быть вызван только из статуса PENDING
        """
        if self.status != ReportStatus.PENDING:
            raise ValueError(f"Cannot start processing from status {self.status}")
        self.status = ReportStatus.PROCESSING
        self.started_at = datetime.now(timezone.utc)

    def complete(self, file_key: str) -> None:
        """
        Отмечает успешное завершение генерации
        Сохраняет ключ файла в S3
        Может быть вызван только из статуса PROCESSING
        """
        if self.status != ReportStatus.PROCESSING:
            raise ValueError(f"Cannot complete from status {self.status}")
        self.status = ReportStatus.COMPLETED
        self.file_key = file_key
        self.completed_at = datetime.now(timezone.utc)

    def fail(self, error_message: str) -> None:
        """
        Отмечает ошибку при генерации
        Сохраняет сообщение об ошибке
        Может быть вызван только из статуса PROCESSING
        """
        if self.status != ReportStatus.PROCESSING:
            raise ValueError(f"Cannot fail from status {self.status}")
        self.status = ReportStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now(timezone.utc)

    def is_finished(self) -> bool:
        """Завершена ли задача (успешно или с ошибкой)."""
        return self.status in (ReportStatus.COMPLETED, ReportStatus.FAILED)

    def can_download(self) -> bool:
        """Можно ли скачать файл (только для COMPLETED с наличием file_key)."""
        return self.status == ReportStatus.COMPLETED and self.file_key is not None

    def has_database_source(self) -> bool:
        """Использует ли задача источник данных из БД."""
        return self.database_source is not None

    def has_inline_data(self) -> bool:
        """Использует ли задача переданные данные."""
        return self.inline_data is not None
