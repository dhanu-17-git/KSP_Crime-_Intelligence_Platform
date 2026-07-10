import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from app.core.config import get_settings


class JsonFormatter(logging.Formatter):
    """Minimal structured JSON formatter for AppSail-friendly stdout logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key in ("request_id", "event", "path", "method", "status_code", "duration_ms"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        details = getattr(record, "details", None)
        if details is not None:
            payload["details"] = details

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging() -> None:
    settings = get_settings()
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(settings.log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)

    logging.getLogger("uvicorn.access").disabled = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


audit_logger = get_logger("app.audit")
ai_logger = get_logger("app.ai")
auth_logger = get_logger("app.auth")
report_logger = get_logger("app.reports")


def log_login_attempt(user_identifier: str, success: bool, request_id: str | None = None) -> None:
    auth_logger.info(
        "Login attempt recorded",
        extra={
            "event": "auth.login_attempt",
            "request_id": request_id,
            "details": {"user_identifier": user_identifier, "success": success},
        },
    )


def log_ai_query(query_type: str, user_id: str, request_id: str | None = None) -> None:
    ai_logger.info(
        "AI query recorded",
        extra={
            "event": "ai.query",
            "request_id": request_id,
            "details": {"query_type": query_type, "user_id": user_id},
        },
    )


def log_report_generation(report_type: str, user_id: str, request_id: str | None = None) -> None:
    report_logger.info(
        "Report generation recorded",
        extra={
            "event": "report.generation",
            "request_id": request_id,
            "details": {"report_type": report_type, "user_id": user_id},
        },
    )


def log_audit_event(action: str, actor_id: str, request_id: str | None = None) -> None:
    audit_logger.info(
        "Audit event recorded",
        extra={
            "event": "audit.event",
            "request_id": request_id,
            "details": {"action": action, "actor_id": actor_id},
        },
    )
