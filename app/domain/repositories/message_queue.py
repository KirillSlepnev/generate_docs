from abc import ABC, abstractmethod
from uuid import UUID


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
