"""JobFlow API entrypoint."""

from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    """Return basic service information."""

    return {"service": settings.app_name, "status": "running"}


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Return the API process health status."""

    return {"status": "ok"}
