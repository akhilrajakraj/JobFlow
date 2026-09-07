"""HTTP middleware for request correlation and access logs."""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("jobflow.http")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request ID and emit a structured access log."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request completed",
            extra={
                "request_id": request_id,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            },
        )
        return response
