from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.core.logging import get_logger
from src.domain.common.exceptions import (
    AlreadyExistsError,
    DoesNotExistError,
    DomainException,
    EmptyFieldError,
    InvalidDateRangeError,
    InvalidStateError,
    InvalidValueError,
    MultipleFoundError,
    RepositoryOperationError,
)
from src.domain.webhooks.exceptions import WebhookSubscriptionInvalidEventsError, WebhookSubscriptionInvalidUrlError

logger = get_logger("exception_handler")


async def does_not_exist_error_handler(request: Request, exc: DoesNotExistError) -> JSONResponse:
    logger.info(f"Resource not found: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def already_exists_error_handler(request: Request, exc: AlreadyExistsError) -> JSONResponse:
    logger.warning(f"Resource already exists: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def invalid_value_error_handler(request: Request, exc: InvalidValueError) -> JSONResponse:
    logger.warning(f"Invalid value: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def invalid_state_error_handler(request: Request, exc: InvalidStateError) -> JSONResponse:
    logger.warning(f"Invalid state: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def empty_field_error_handler(request: Request, exc: EmptyFieldError) -> JSONResponse:
    logger.warning(f"Empty field: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def invalid_date_range_error_handler(request: Request, exc: InvalidDateRangeError) -> JSONResponse:
    logger.warning(f"Invalid date range: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def webhook_invalid_url_error_handler(request: Request, exc: WebhookSubscriptionInvalidUrlError) -> JSONResponse:
    logger.warning(f"Invalid webhook URL: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def webhook_invalid_events_error_handler(
    request: Request, exc: WebhookSubscriptionInvalidEventsError
) -> JSONResponse:
    logger.warning(f"Invalid webhook events: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def multiple_found_error_handler(request: Request, exc: MultipleFoundError) -> JSONResponse:
    logger.exception(f"Multiple records found: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка: найдено несколько записей вместо одной"},
    )


async def repository_operation_error_handler(request: Request, exc: RepositoryOperationError) -> JSONResponse:
    logger.exception(f"Repository operation error: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ошибка операции с хранилищем данных"},
    )


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    logger.info(f"Domain exception: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )
