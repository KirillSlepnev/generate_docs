from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import List

from app.domain.models.value_objects import (
    ColumnDefinition,
    OutputFormat,
    StylingConfig,
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
