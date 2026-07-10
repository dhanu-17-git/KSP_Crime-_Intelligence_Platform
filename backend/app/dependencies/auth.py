from collections.abc import Iterable

from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer

from app.core.config import get_settings
from app.core.security import Permission, Role, decode_access_token
from app.schemas.user import CurrentUser
from app.utils.exceptions import AuthenticationError, AuthorizationError

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_prefix}/auth/login",
    auto_error=False
)


async def get_current_user(token: str | None = Security(oauth2_scheme)) -> CurrentUser:
    if token is None:
        # Development/demo fallback to allow seamless API access from UI
        return CurrentUser(
            id="1001",
            role=Role.OFFICER,
            permissions=[Permission.RUN_AI_QUERIES, Permission.READ_CASES],
        )

    payload = decode_access_token(token)
    role = payload.get("role")
    permissions = payload.get("permissions", [])

    try:
        parsed_role = Role(role)
        parsed_permissions = [Permission(permission) for permission in permissions]
    except ValueError as exc:
        raise AuthenticationError("Authentication token contains invalid RBAC claims") from exc

    return CurrentUser(
        id=str(payload["sub"]),
        role=parsed_role,
        permissions=parsed_permissions,
    )


def require_roles(allowed_roles: Iterable[Role]):
    allowed = set(allowed_roles)

    async def checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed:
            raise AuthorizationError("User role is not permitted to access this resource")
        return current_user

    return checker


def require_permissions(required_permissions: Iterable[Permission]):
    required = set(required_permissions)

    async def checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not required.issubset(set(current_user.permissions)):
            raise AuthorizationError("User is missing required permissions")
        return current_user

    return checker
