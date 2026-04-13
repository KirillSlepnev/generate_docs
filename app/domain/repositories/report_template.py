from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.models.report_template import ReportTemplate


class ITemplateRepository(ABC):
    @abstractmethod
    async def add(self, template: ReportTemplate) -> None:
        """Сохраняет новый шаблон в хранилище"""
        pass

    @abstractmethod
    async def get_by_id(self, template_id: UUID) -> ReportTemplate | None:
        """
        Возвращает шаблон по его идентификатору
        Если шаблон не найден — возвращает None
        """
        pass

    @abstractmethod
    async def list_by_user(
        self, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[ReportTemplate]:
        """
        Возвращает список шаблонов, принадлежащих пользователю
        Поддерживает пагинацию через limit и offset
        """
        pass

    @abstractmethod
    async def update(self, template: ReportTemplate) -> None:
        """Обновляет существующий шаблон"""
        pass

    @abstractmethod
    async def delete(self, template_id: UUID) -> None:
        """Удаляет шаблон по идентификатору"""
        pass
