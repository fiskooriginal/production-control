from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.application.common.exceptions import ApplicationException, BusinessRuleViolationException, ValidationException
from src.core.logging import get_logger

logger = get_logger("exception_handler")


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
