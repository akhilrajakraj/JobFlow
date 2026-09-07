"""JobFlow API entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import check_database_connection, engine
from app.core.redis import check_redis_connection, close_redis


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage application-owned database and Redis resources."""

    yield
    await engine.dispose()
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    """Return basic service information."""

    return {"service": settings.app_name, "status": "running"}


@app.get("/health", tags=["system"])
async def health() -> dict[str, str | dict[str, str]]:
    """Return API, PostgreSQL, and Redis health status."""

    database_ok = await check_database_connection()
    redis_ok = await check_redis_connection()
    status = "ok" if database_ok and redis_ok else "degraded"

    return {
        "status": status,
        "dependencies": {
            "postgres": "ok" if database_ok else "unavailable",
            "redis": "ok" if redis_ok else "unavailable",
        },
    }
