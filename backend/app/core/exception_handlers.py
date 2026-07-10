from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.schemas.response import ApiError
from app.utils.exceptions import AppError, AuthenticationError, AuthorizationError
from app.utils.responses import error_response

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(AuthenticationError, app_exception_handler)
    app.add_exception_handler(AuthorizationError, app_exception_handler)
    app.add_exception_handler(AppError, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unknown_exception_handler)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [
        ApiError(
            code="VALIDATION_ERROR",
            message=str(error.get("msg", "Invalid value")),
            field=".".join(str(part) for part in error.get("loc", [])),
        )
        for error in exc.errors()
    ]
    return _json_response(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Request validation failed",
        errors=errors,
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception(
        "Database operation failed",
        extra={"request_id": getattr(request.state, "request_id", None), "event": "database.exception"},
    )
    return _json_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Database operation failed",
        errors=[ApiError(code="DATABASE_ERROR", message="A database error occurred")],
    )


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    return _json_response(
        request=request,
        status_code=exc.status_code,
        message=exc.message,
        errors=[ApiError(code=exc.error_code, message=exc.message)],
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    error_code = "HTTP_ERROR"
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        error_code = "AUTHENTICATION_ERROR"
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        error_code = "AUTHORIZATION_ERROR"

    return _json_response(
        request=request,
        status_code=exc.status_code,
        message=str(exc.detail),
        errors=[ApiError(code=error_code, message=str(exc.detail))],
    )


async def unknown_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled application exception",
        extra={"request_id": getattr(request.state, "request_id", None), "event": "app.exception"},
    )
    return _json_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Internal server error",
        errors=[ApiError(code="INTERNAL_SERVER_ERROR", message="An unexpected error occurred")],
    )


def _json_response(
    request: Request,
    status_code: int,
    message: str,
    errors: list[ApiError],
) -> JSONResponse:
    body = error_response(request=request, message=message, errors=errors)
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json"),
        headers={"x-request-id": body.request_id},
    )
