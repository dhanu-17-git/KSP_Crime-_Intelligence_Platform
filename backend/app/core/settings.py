from functools import cached_property

from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "KSP Crime Intelligence API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "ksp_crime_intel"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    database_echo: bool = False
    database_pool_size: int = 10
    database_max_overflow: int = 20

    jwt_secret_key: str = "change-me-before-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    ai_provider: str = "none"
    gemini_api_key: str | None = None
    gemini_model_name: str = "gemini-flash-latest"

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def database_url(self) -> str:
        import os, urllib.parse
        env_url = os.environ.get("DATABASE_URL")
        if env_url:
            url = env_url
            if url.startswith("sqlite"):
                return url
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            parsed = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed.query)
            # Retain only valid asyncpg query params
            filtered_params = {}
            if "sslmode" in query_params or "ssl" in query_params:
                filtered_params["ssl"] = "require"
            new_query = urllib.parse.urlencode(filtered_params)
            sanitized = urllib.parse.urlunparse((
                parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment
            ))
            return sanitized

        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.2)
                s.connect((self.postgres_host, self.postgres_port))
        except (socket.timeout, ConnectionRefusedError, OSError):
            return "sqlite+aiosqlite:///ksp_crime_intel.db"

        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                path=f"/{self.postgres_db}",
            )
        )

