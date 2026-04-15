from minio import Minio

from app.domain.repositories.file_storage import IFileStorage
from app.config import settings


class MinioStorage(IFileStorage):
    def __init__(self):
        self._client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self._bucket = settings.minio_bucket

    async def upload(self, file_data: bytes, key: str, content_type: str) -> str:
        try:
            import io

            data_stream = io.BytesIO(file_data)

            self._client.put_object(
                bucket_name=self._bucket,
                object_name=key,
                data=data_stream,
                length=len(file_data),
                content_type=content_type,
            )

            return key

        except Exception as e:
            raise RuntimeError(f"Error uploading file: {str(e)}")

    async def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            url = self._client.presigned_get_object(
                bucket_name=self._bucket,
                object_name=key,
                expires=expires_in,
            )

            return url
        except Exception as e:
            raise RuntimeError(f"Error getting url: {str(e)}")
