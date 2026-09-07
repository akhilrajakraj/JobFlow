"""Redis client configuration."""

from redis.asyncio import Redis

from app.core.config import settings


redis_client = Redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


async def check_redis_connection() -> bool:
    """Return whether Redis accepts a ping."""

    try:
        return bool(await redis_client.ping())
    except Exception:
        return False


async def close_redis() -> None:
    """Close the shared Redis connection pool."""

    await redis_client.aclose()
