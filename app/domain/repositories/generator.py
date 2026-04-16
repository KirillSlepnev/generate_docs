from abc import abstractmethod, ABC
from typing import Any

from app.domain.models.value_objects import ColumnDefinition, StylingConfig


class IFileGenerate(ABC):
    """Интерфейс для генерации отчета"""

    @abstractmethod
    async def generate(
        self,
        data: list[dict[str, Any]],
        columns: list[ColumnDefinition],
        styling: StylingConfig | None = None,
    ) -> bytes:
        """
        Функция для генерации отчета

        Args:
            data: список словарей с данными для отчета
            columns: список данных для определения параметров колонки, объекты ColumnDefinition
            styling: визуальные настройки документа, объекты StylingConfig

        Returns:
            bytes: бинарные данные сгенерированного отчета
        """
        pass
