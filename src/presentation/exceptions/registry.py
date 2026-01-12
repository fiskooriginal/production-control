from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from src.application.common.exceptions import (
    ApplicationException,
    BusinessRuleViolationException,
    ValidationException,
)
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
from src.domain.webhooks.exceptions import (
    WebhookSubscriptionInvalidEventsError,
    WebhookSubscriptionInvalidUrlError,
)
from src.infrastructure.common.exceptions import (
    ConnectionException,
    DatabaseException,
    InfrastructureException,
    MappingException,
    OutboxRepositoryException,
)
from src.presentation.exceptions.base import PresentationException
from src.presentation.exceptions.handlers import application, base, domain, infrastructure, presentation
from src.presentation.exceptions.serialization import SerializationException


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует все обработчики исключений для FastAPI приложения в правильном порядке (от конкретных к общим)"""

    # Domain layer exceptions (конкретные исключения регистрируются перед базовыми)
    app.add_exception_handler(DoesNotExistError, domain.does_not_exist_error_handler)
    app.add_exception_handler(AlreadyExistsError, domain.already_exists_error_handler)
    app.add_exception_handler(InvalidValueError, domain.invalid_value_error_handler)
    app.add_exception_handler(InvalidStateError, domain.invalid_state_error_handler)
    app.add_exception_handler(EmptyFieldError, domain.empty_field_error_handler)
    app.add_exception_handler(InvalidDateRangeError, domain.invalid_date_range_error_handler)
    app.add_exception_handler(WebhookSubscriptionInvalidUrlError, domain.webhook_invalid_url_error_handler)
    app.add_exception_handler(WebhookSubscriptionInvalidEventsError, domain.webhook_invalid_events_error_handler)
    app.add_exception_handler(MultipleFoundError, domain.multiple_found_error_handler)
    app.add_exception_handler(RepositoryOperationError, domain.repository_operation_error_handler)
    app.add_exception_handler(DomainException, domain.domain_exception_handler)

    # Application layer exceptions
    app.add_exception_handler(ValidationException, application.validation_exception_handler)
    app.add_exception_handler(BusinessRuleViolationException, application.business_rule_violation_handler)
    app.add_exception_handler(ApplicationException, application.application_exception_handler)

    # Infrastructure layer exceptions
    app.add_exception_handler(DatabaseException, infrastructure.database_exception_handler)
    app.add_exception_handler(ConnectionException, infrastructure.connection_exception_handler)
    app.add_exception_handler(MappingException, infrastructure.mapping_exception_handler)
    app.add_exception_handler(OutboxRepositoryException, infrastructure.outbox_repository_exception_handler)
    app.add_exception_handler(InfrastructureException, infrastructure.infrastructure_exception_handler)

    # Presentation layer exceptions
    app.add_exception_handler(SerializationException, presentation.serialization_exception_handler)
    app.add_exception_handler(PresentationException, presentation.presentation_exception_handler)
    app.add_exception_handler(ValidationError, presentation.pydantic_validation_error_handler)
    app.add_exception_handler(RequestValidationError, presentation.request_validation_error_handler)

    # Unexpected exceptions (должен быть последним)
    app.add_exception_handler(Exception, base.unexpected_error_handler)
