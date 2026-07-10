from typing import TypeVar

from fastapi import Request

from app.schemas.response import ApiError, ApiResponse

DataT = TypeVar("DataT")


def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", request.headers.get("x-request-id", "unknown"))


def success_response(request: Request, message: str, data: DataT | None = None) -> ApiResponse[DataT]:
    return ApiResponse(
        success=True,
        message=message,
        data=data,
        errors=[],
        request_id=get_request_id(request),
    )


def error_response(
    request: Request,
    message: str,
    errors: list[ApiError],
) -> ApiResponse[None]:
    return ApiResponse(
        success=False,
        message=message,
        data=None,
        errors=errors,
        request_id=get_request_id(request),
    )
