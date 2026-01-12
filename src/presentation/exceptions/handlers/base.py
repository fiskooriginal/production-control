from typing import Protocol, TypeVar

from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.core.logging import get_logger

logger = get_logger("exception_handler")

ExceptionType = TypeVar("ExceptionType", bound=Exception)


class ExceptionHandler(Protocol[ExceptionType]):
    """Протокол для обработчиков исключений"""

    async def __call__(self, request: Request, exc: ExceptionType) -> JSONResponse:
        """Обрабатывает исключение и возвращает JSONResponse"""
        ...


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unexpected error: {type(exc).__name__} {exc!s} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера"},
    )
