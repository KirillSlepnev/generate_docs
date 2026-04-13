from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.models.report import Report


class IReportRepository(ABC):
    @abstractmethod
    async def add(self, report: Report) -> None:
        """Сохраняет новую задачу в хранилище"""
        pass

    @abstractmethod
    async def get_by_id(self, report_id: UUID) -> Report | None:
        """
        Возвращает задачу по её идентификатору
        Если задача не найдена — возвращает None
        """
        pass

    @abstractmethod
    async def update(self, report: Report) -> None:
        """Обновляет существующую задачу (статус, file_key, error_message)"""
        pass

    @abstractmethod
    async def list_by_user(
        self, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[Report]:
        """
        Возвращает список задач, принадлежащих пользователю.
        Поддерживает пагинацию через limit и offset
        Задачи сортируются по created_at (сначала новые)
        """
        pass
