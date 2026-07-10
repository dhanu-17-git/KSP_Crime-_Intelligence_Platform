from fastapi import APIRouter, Request, status

from app.schemas.response import ApiResponse
from app.utils.responses import success_response

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=ApiResponse[dict[str, str]], status_code=status.HTTP_200_OK)
async def health_check(request: Request) -> ApiResponse[dict[str, str]]:
    """Return service health without touching business modules."""
    return success_response(
        request=request,
        message="Service is healthy",
        data={"status": "ok"},
    )
