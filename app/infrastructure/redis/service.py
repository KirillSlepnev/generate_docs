import json
from typing import Any, Callable

from app.infrastructure.redis.client import get_client


class CacheService:
    @staticmethod
    def _build_key(prefix: str, **kwargs) -> str:
        parts = [prefix]

        for key, value in sorted(kwargs.items()):
            parts.append(f"{key}:{value}")

        return ":".join(parts)

    @staticmethod
    async def get(key: str) -> str | None:
        redis = await get_client()
        data = await redis.get(key)

        if data is None:
            return None

        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data

    @staticmethod
    async def set(key: str, value: Any, expire: int | None = None) -> None:
        redis = await get_client()

        if expire:
            await redis.setex(key, expire, str(value))
        else:
            await redis.set(key, str(value))

    @staticmethod
    async def delete(key: str) -> None:
        redis = await get_client()

        await redis.delete(key)

    @staticmethod
    async def delete_pattern(pattern: str) -> None:
        redis = await get_client()
        cursor = 0

        while True:
            cursor, keys = await redis.scan(cursor, pattern, count=100)

            if keys:
                await CacheService.delete(*keys)

            if cursor == 0:
                break

    @staticmethod
    async def get_or_set(
        key: str, factory: Callable[[], Any], expire: int | None = None
    ) -> Any:
        cached = CacheService.get(key)
        if cached is not None:
            return cached

        value = await factory()
        await CacheService.set(key, value, expire)
        return value


class CacheKeys:
    REPORT_STATUS = "report:status"
    REPORT_DOWNLOAD_URL = "report:download_url"
    REPORT_LIST = "report:list"
    TEMPLATE = "template"
    TEMPLATE_LIST = "template:list"

    @staticmethod
    def report_status(report_id: str, user_id: str) -> str:
        return CacheService._build_key(
            CacheKeys.REPORT_STATUS, report_id=report_id, user_id=user_id
        )

    @staticmethod
    def report_download_url(report_id: str, user_id: str) -> str:
        return CacheService._build_key(
            CacheKeys.REPORT_DOWNLOAD_URL,
            report_id=report_id,
            user_id=user_id,
        )

    @staticmethod
    def report_list(user_id: str, limit: int, offset: int) -> str:
        return CacheService._build_key(
            CacheKeys.REPORT_LIST,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def report_list_pattern(user_id: str) -> str:
        """Паттерн для инвалидации всех кэшей списка отчетов пользователя"""
        return f"{CacheKeys.REPORT_LIST}:user_id:{user_id}:*"

    @staticmethod
    def template(template_id: str, user_id: str) -> str:
        return CacheService._build_key(
            CacheKeys.TEMPLATE,
            template_id=template_id,
            user_id=user_id,
        )

    @staticmethod
    def template_list(user_id: str, limit: int, offset: int) -> str:
        return CacheService._build_key(
            CacheKeys.TEMPLATE_LIST,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def template_list_pattern(user_id: str) -> str:
        """Паттерн для инвалидации всех кэшей списка шаблонов пользователя"""
        return f"{CacheKeys.TEMPLATE_LIST}:user_id:{user_id}:*"
