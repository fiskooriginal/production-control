from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.core.logging import get_logger
from src.infrastructure.common.exceptions import (
    ConnectionException,
    DatabaseException,
    InfrastructureException,
    MappingException,
    OutboxRepositoryException,
)

logger = get_logger("exception_handler")


async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    logger.exception(f"Database error: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ошибка при работе с базой данных"},
    )


async def connection_exception_handler(request: Request, exc: ConnectionException) -> JSONResponse:
    logger.exception(f"Connection error: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Ошибка подключения к внешнему сервису"},
    )


async def mapping_exception_handler(request: Request, exc: MappingException) -> JSONResponse:
    logger.exception(f"Mapping error: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ошибка преобразования данных"},
    )


async def outbox_repository_exception_handler(request: Request, exc: OutboxRepositoryException) -> JSONResponse:
    logger.exception(f"Outbox repository error: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ошибка при работе с outbox репозиторием"},
    )


async def infrastructure_exception_handler(request: Request, exc: InfrastructureException) -> JSONResponse:
    logger.exception(f"Infrastructure error: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка инфраструктуры"},
    )
