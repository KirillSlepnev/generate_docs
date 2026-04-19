import io

import aioboto3

from app.domain.repositories.file_storage import IFileStorage
from app.config import settings


class S3Storage(IFileStorage):
    def __init__(self):
        self._endpoint_url = settings.s3_endpoint_url
        self._access_key = settings.s3_access_key_id
        self._secret_key = settings.s3_secret_access_key
        self._bucket = settings.s3_bucket_name
        self._region = settings.s3_region
        self._public_endpoint = settings.s3_public_endpoint_url
        self._secure = settings.s3_secure

    async def upload(self, file_data: bytes, key: str, content_type: str) -> str:
        try:
            session = aioboto3.Session()

            async with session.client(
                "s3",
                endpoint_url=self._endpoint_url,
                aws_access_key_id=self._access_key,
                aws_secret_access_key=self._secret_key,
                region_name=self._region,
                use_ssl=self._secure,
            ) as s3:
                data_stream = io.BytesIO(file_data)
                await s3.upload_fileobj(
                    Fileobj=data_stream,
                    Bucket=self._bucket,
                    Key=key,
                    ExtraArgs={"ContentType": content_type},
                )
                return key
        except Exception as e:
            raise RuntimeError(f"Error uploading file: {str(e)}")

    async def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            session = aioboto3.Session()
            async with session.client(
                "s3",
                endpoint_url=self._endpoint_url,
                aws_access_key_id=self._access_key,
                aws_secret_access_key=self._secret_key,
                region_name=self._region,
                use_ssl=self._secure,
            ) as s3:
                url = await s3.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={
                        "Bucket": self._bucket,
                        "Key": key,
                    },
                    ExpiresIn=expires_in,
                )

                if self._public_endpoint != self._endpoint_url:
                    url = url.replace(self._endpoint_url, self._public_endpoint)

                return url
        except Exception as e:
            raise RuntimeError(f"Error getting url: {str(e)}")
