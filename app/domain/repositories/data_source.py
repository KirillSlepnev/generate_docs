from abc import ABC, abstractmethod
from typing import List

from app.domain.models.value_objects import DatabaseSource


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
