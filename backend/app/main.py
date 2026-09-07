"""JobFlow API entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.jobs import router as jobs_router
from app.api.routes.workers import router as workers_router
from app.core.config import settings
from app.core.database import check_database_connection, engine
from app.core.redis import check_redis_connection, close_redis
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage application-owned resources and development schema."""

    await init_db()
    yield
    await engine.dispose()
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(workers_router, prefix="/api/v1")


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "running"}


@app.get("/health", tags=["system"])
async def health() -> dict[str, str | dict[str, str]]:
    database_ok = await check_database_connection()
    redis_ok = await check_redis_connection()
    service_status = "ok" if database_ok and redis_ok else "degraded"
    return {
        "status": service_status,
        "dependencies": {
            "postgres": "ok" if database_ok else "unavailable",
            "redis": "ok" if redis_ok else "unavailable",
        },
    }
