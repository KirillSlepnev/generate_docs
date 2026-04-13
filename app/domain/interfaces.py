# interfaces.py
from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from app.domain.entities import ReportTemplate, Report
from app.domain.value_objects import DatabaseSource


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


class IFileStorage(ABC):
    @abstractmethod
    async def upload(self, file_data: bytes, key: str, content_type: str) -> str:
        """
        Загружает файл в хранилище

        Args:
            file_data: бинарные данные файла
            key: путь к файлу в хранилище (например, 'user_id/2026/04/report_id.xlsx')
            content_type: MIME-тип файла

        Returns:
            Ключ загруженного файла
        """
        pass

    @abstractmethod
    async def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Генерирует временную ссылку для скачивания файла

        Args:
            key: путь к файлу в хранилище
            expires_in: время жизни ссылки в секундах (по умолчанию 1 час)

        Returns:
            URL для скачивания файла
        """
        pass


class IMessageBus(ABC):
    """Интерфейс для отправки сообщений в очередь"""

    @abstractmethod
    async def publish_generate_report_task(self, report_id: UUID) -> None:
        """
        Публикует задачу на генерацию отчета в очередь.

        Args:
            report_id: идентификатор задачи, которую нужно обработать
        """
        pass


class IDataSource(ABC):
    @abstractmethod
    async def fetch_data(self, source: DatabaseSource) -> List[dict]:
        """
        Извлекает данные из таблицы согласно переданным параметрам.

        Args:
            source: параметры запроса (таблица, поля, фильтры, диапазон дат)

        Returns:
            Список словарей с данными, где ключи соответствуют source.fields
        """
        pass
