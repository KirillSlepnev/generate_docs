from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import date


class OutputFormat(str, Enum):
    EXCEL = "excel"
    PDF = "pdf"


class ReportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ColumnDefinition:
    """Описание колонки в отчете"""
    field: str
    header: str
    width: int | None = None
    format: str | None = None


@dataclass(frozen=True)
class StylingConfig:
    """Настройки оформления отчета"""
    header_bg_color: str | None = None
    header_font_color: str | None = None
    font_size: int | None = None
    orientation: str | None = None


@dataclass(frozen=True)
class DatabaseSource:
    """Источник данных из БД"""
    table: str
    fields: List[str]
    date_field: str
    date_from: date
    date_to: date
    filters: Dict[str, Any] | None = None


@dataclass(frozen=True)
class InlineData:
    """Данные, переданные пользователем"""
    data: List[Dict[str, Any]]
    
    @property
    def row_count(self) -> int:
        return len(self.data)
