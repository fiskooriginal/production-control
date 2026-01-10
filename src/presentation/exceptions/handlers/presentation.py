from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.core.logging import get_logger
from src.presentation.exceptions.base import PresentationException
from src.presentation.exceptions.serialization import SerializationException

logger = get_logger("exception_handler")


async def serialization_exception_handler(request: Request, exc: SerializationException) -> JSONResponse:
    logger.warning(f"Serialization error: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def presentation_exception_handler(request: Request, exc: PresentationException) -> JSONResponse:
    logger.warning(f"Presentation error: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


async def pydantic_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    logger.warning(f"Pydantic validation error path={request.url.path} errors={exc.errors()!r}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Ошибка валидации данных", "errors": exc.errors()},
    )


async def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning(f"Request validation error path={request.url.path} errors={exc.errors()!r}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Ошибка валидации запроса", "errors": exc.errors()},
    )
