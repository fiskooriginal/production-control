from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.application.exceptions import (
    ApplicationException,
    BusinessRuleViolationException,
    ValidationException,
)
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
)
from src.presentation.exceptions import (
    PresentationException,
    SerializationException,
)


async def does_not_exist_error_handler(request: Request, exc: DoesNotExistError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def already_exists_error_handler(request: Request, exc: AlreadyExistsError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def invalid_value_error_handler(request: Request, exc: InvalidValueError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def invalid_state_error_handler(request: Request, exc: InvalidStateError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def empty_field_error_handler(request: Request, exc: EmptyFieldError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def invalid_date_range_error_handler(request: Request, exc: InvalidDateRangeError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def webhook_invalid_url_error_handler(request: Request, exc: WebhookSubscriptionInvalidUrlError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def webhook_invalid_events_error_handler(
    request: Request, exc: WebhookSubscriptionInvalidEventsError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def multiple_found_error_handler(request: Request, exc: MultipleFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка: найдено несколько записей вместо одной"},
    )


async def repository_operation_error_handler(request: Request, exc: RepositoryOperationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ошибка операции с хранилищем данных"},
    )


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def business_rule_violation_handler(request: Request, exc: BusinessRuleViolationException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def application_exception_handler(request: Request, exc: ApplicationException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ошибка при работе с базой данных"},
    )


async def connection_exception_handler(request: Request, exc: ConnectionException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Ошибка подключения к внешнему сервису"},
    )


async def mapping_exception_handler(request: Request, exc: MappingException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ошибка преобразования данных"},
    )


async def infrastructure_exception_handler(request: Request, exc: InfrastructureException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка инфраструктуры"},
    )


async def serialization_exception_handler(request: Request, exc: SerializationException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def presentation_exception_handler(request: Request, exc: PresentationException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


async def pydantic_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Ошибка валидации данных", "errors": exc.errors()},
    )


async def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Ошибка валидации запроса", "errors": exc.errors()},
    )


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
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
    app.add_exception_handler(InfrastructureException, infrastructure_exception_handler)

    # Presentation exceptions
    app.add_exception_handler(SerializationException, serialization_exception_handler)
    app.add_exception_handler(PresentationException, presentation_exception_handler)

    # Pydantic exceptions
    app.add_exception_handler(ValidationError, pydantic_validation_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)

    # Unexpected exceptions
    app.add_exception_handler(Exception, unexpected_error_handler)
