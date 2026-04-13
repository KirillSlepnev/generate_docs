from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List
from datetime import date


class OutputFormat(str, Enum):
    """Формат файла, который будет сгенерирован"""

    EXCEL = "excel"
    PDF = "pdf"


class ReportStatus(str, Enum):
    """
    Жизненный цикл задачи генерации отчета

    Args:
        PENDING: задача создана, но еще не взята воркером
        PROCESSING: воркер начал генерацию файла
        COMPLETED: файл успешно сгенерирован и загружен в S3
        FAILED: произошла ошибка, детали в error_message
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ColumnDefinition:
    """
    Связь между полем в словаре данных и его представлением в отчете

    Args:
        field: ключ в словаре с данными (например, 'created_at')
        header: заголовок колонки в Excel/PDF (например, 'Дата создания')
        width: ширина колонки в условных единицах (опционально)
        format: строка форматирования (опционально)
                для чисел: '#,##0.00'
                для дат: 'DD.MM.YYYY'
    """

    field: str
    header: str
    width: int | None = None
    format: str | None = None


@dataclass(frozen=True)
class StylingConfig:
    """
    Визуальные настройки итогового документа
    Применяются при генерации Excel или PDF

    Args:
        header_bg_color: HEX, например '#4472C4'
        header_font_color: HEX, например '#FFFFFF'
        font_size: в пунктах
        orientation: 'portrait' или 'landscape' для PDF
    """

    header_bg_color: str | None = None
    header_font_color: str | None = None
    font_size: int | None = None
    orientation: str | None = None


@dataclass(frozen=True)
class DatabaseSource:
    """
    Параметры для извлечения данных из таблицы базы данных

    Args:
        table: имя таблицы (например, 'orders')
        fields: список полей для SELECT (например, ['id', 'amount', 'created_at'])
        date_field: поле, по которому фильтруется диапазон дат
        date_from: начало периода (включительно)
        date_to: конец периода (включительно)
        filters: дополнительные условия WHERE в виде словаря {field: value}
                значение может быть скаляром или {"gte": 100, "lte": 500}
    """

    table: str
    fields: List[str]
    date_field: str
    date_from: date
    date_to: date
    filters: Dict[str, Any] | None = None


@dataclass(frozen=True)
class InlineData:
    """
    Данные, переданные пользователем напрямую в запросе
    Используется когда не нужно обращаться к базе данных

    Args:
        data: список словарей, каждый словарь — одна строка отчета
            ключи словаря должны соответствовать ColumnDefinition.field
    """

    data: List[Dict[str, Any]]

    def row_count(self) -> int:
        return len(self.data)
