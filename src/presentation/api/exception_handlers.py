from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.application.exceptions import (
    ApplicationException,
    BusinessRuleViolationException,
    ValidationException,
)
from src.core.logging import get_logger
from src.domain.shared.exceptions import (
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
from src.domain.webhooks.exceptions import (
    WebhookSubscriptionInvalidEventsError,
    WebhookSubscriptionInvalidUrlError,
)
from src.infrastructure.exceptions import (
    ConnectionException,
    DatabaseException,
    InfrastructureException,
    MappingException,
    OutboxRepositoryException,
)
from src.presentation.exceptions import (
    PresentationException,
    SerializationException,
)

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


async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    logger.warning(f"Validation error: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def business_rule_violation_handler(request: Request, exc: BusinessRuleViolationException) -> JSONResponse:
    logger.warning(f"Business rule violation: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def application_exception_handler(request: Request, exc: ApplicationException) -> JSONResponse:
    logger.warning(f"Application exception: {exc.message} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


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


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unexpected error: {type(exc).__name__} {exc!s} path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует все обработчики исключений для FastAPI приложения"""
    # Domain exceptions
    app.add_exception_handler(DoesNotExistError, does_not_exist_error_handler)
    app.add_exception_handler(AlreadyExistsError, already_exists_error_handler)
    app.add_exception_handler(InvalidValueError, invalid_value_error_handler)
    app.add_exception_handler(InvalidStateError, invalid_state_error_handler)
    app.add_exception_handler(EmptyFieldError, empty_field_error_handler)
    app.add_exception_handler(InvalidDateRangeError, invalid_date_range_error_handler)
    app.add_exception_handler(WebhookSubscriptionInvalidUrlError, webhook_invalid_url_error_handler)
    app.add_exception_handler(WebhookSubscriptionInvalidEventsError, webhook_invalid_events_error_handler)
    app.add_exception_handler(MultipleFoundError, multiple_found_error_handler)
    app.add_exception_handler(RepositoryOperationError, repository_operation_error_handler)
    app.add_exception_handler(DomainException, domain_exception_handler)

    # Application exceptions
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(BusinessRuleViolationException, business_rule_violation_handler)
    app.add_exception_handler(ApplicationException, application_exception_handler)

    # Infrastructure exceptions
    app.add_exception_handler(DatabaseException, database_exception_handler)
    app.add_exception_handler(ConnectionException, connection_exception_handler)
    app.add_exception_handler(MappingException, mapping_exception_handler)
    app.add_exception_handler(OutboxRepositoryException, outbox_repository_exception_handler)
    app.add_exception_handler(InfrastructureException, infrastructure_exception_handler)

    # Presentation exceptions
    app.add_exception_handler(SerializationException, serialization_exception_handler)
    app.add_exception_handler(PresentationException, presentation_exception_handler)

    # Pydantic exceptions
    app.add_exception_handler(ValidationError, pydantic_validation_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)

    # Unexpected exceptions
    app.add_exception_handler(Exception, unexpected_error_handler)
