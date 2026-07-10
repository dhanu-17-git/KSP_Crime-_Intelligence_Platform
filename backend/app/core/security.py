from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.utils.exceptions import AuthenticationError


class Role(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    INVESTIGATOR = "investigator"
    ANALYST = "analyst"
    OFFICER = "officer"
    VIEWER = "viewer"


class Permission(StrEnum):
    READ_CASES = "read:cases"
    WRITE_CASES = "write:cases"
    READ_SUSPECTS = "read:suspects"
    WRITE_SUSPECTS = "write:suspects"
    READ_VEHICLES = "read:vehicles"
    WRITE_VEHICLES = "write:vehicles"
    READ_REPORTS = "read:reports"
    GENERATE_REPORTS = "generate:reports"
    RUN_AI_QUERIES = "run:ai_queries"
    MANAGE_USERS = "manage:users"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, claims: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expires_at,
        "iat": datetime.now(UTC),
    }
    if claims:
        payload.update(claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired authentication token") from exc
    if not payload.get("sub"):
        raise AuthenticationError("Authentication token is missing subject")
    return payload
