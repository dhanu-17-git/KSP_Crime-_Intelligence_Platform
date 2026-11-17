# KSP Crime Intelligence Backend

FastAPI backend foundation for the Karnataka State Police AI Crime Intelligence Platform.

## Scope

This foundation includes:

- FastAPI app factory and health check
- Environment-driven settings
- Async SQLAlchemy PostgreSQL engine/session
- Alembic migration scaffold
- Structured JSON logging
- Request id propagation and request logging middleware
- Unified API response envelope
- Global exception handlers
- JWT, password hashing, RBAC enums, and auth dependencies
- Investigation engine skeleton with swappable AI provider boundary
- Foundation tests

No business modules are implemented yet.

## Local Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/api/v1/health
```

## Database

Configure PostgreSQL in `.env`, then run migrations:

```bash
alembic upgrade head
```

There are intentionally no business tables in the foundation.

## Tests

```bash
pytest
```

## Deployment Notes

The app writes structured logs to stdout and reads configuration from environment variables, keeping it compatible with Docker containers, Kubernetes, and cloud container environments.
