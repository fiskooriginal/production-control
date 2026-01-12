import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logging import get_logger

logger = get_logger("http.middleware.logging")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов и ответов"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        query_params = dict(request.query_params) if request.query_params else {}
        logger.info(f"{request.method} {request.url.path} query_params={query_params}")

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.exception(
                f"{request.method} {request.url.path} failed duration={duration_ms}ms error={type(exc).__name__}"
            )
            raise

        duration_ms = int((time.time() - start_time) * 1000)

        if response.status_code >= 500:
            logger.error(f"{request.method} {request.url.path} status={response.status_code} duration={duration_ms}ms")
        elif response.status_code >= 400:
            logger.warning(
                f"{request.method} {request.url.path} status={response.status_code} duration={duration_ms}ms"
            )
        else:
            logger.info(f"{request.method} {request.url.path} status={response.status_code} duration={duration_ms}ms")

        return response
