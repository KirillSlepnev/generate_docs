from abc import ABC, abstractmethod


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
