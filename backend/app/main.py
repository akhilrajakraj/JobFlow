"""JobFlow API entrypoint."""

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import select

from app.api.routes.auth import router as auth_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.workers import router as workers_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, check_database_connection, engine
from app.core.logging import configure_logging
from app.core.metrics import metrics_response
from app.core.redis import check_redis_connection, close_redis
from app.core.security import hash_password
from app.db.init_db import init_db
from app.models.user import User


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    if settings.environment.lower() not in {"production", "prod"}:
        await init_db()
    async with AsyncSessionLocal() as session:
        admin = await session.scalar(select(User).where(User.username == settings.admin_username))
        if admin is None:
            session.add(
                User(
                    username=settings.admin_username,
                    password_hash=hash_password(settings.admin_password),
                    role="ADMIN",
                )
            )
            await session.commit()
    yield
    await engine.dispose()
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(auth_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(workers_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "running", "version": settings.app_version}


@app.get("/health")
async def health() -> dict[str, str | dict[str, str]]:
    database_ok = await check_database_connection()
    redis_ok = await check_redis_connection()
    return {
        "status": "ok" if database_ok and redis_ok else "degraded",
        "dependencies": {
            "postgres": "ok" if database_ok else "unavailable",
            "redis": "ok" if redis_ok else "unavailable",
        },
    }


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    body, content_type = metrics_response()
    return Response(
        content=body,
        media_type=content_type.split(";", 1)[0],
        headers={"Content-Type": content_type},
    )
