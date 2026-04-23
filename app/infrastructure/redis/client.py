from redis.asyncio import Redis

from app.config import settings


_redis_client: Redis | None = None


async def get_client() -> Redis:
    global _redis_client

    if _redis_client is None:
        _redis_client = Redis.from_url(settings.redis_url, decode_response=True)

    return _redis_client


async def close_redis() -> None:
    global _redis_client

    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None
