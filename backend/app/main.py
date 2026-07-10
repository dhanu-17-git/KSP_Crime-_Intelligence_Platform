from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1 import v1_router
from app.api.investigation import router as investigation_router
from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.middleware.request_logging import RequestLoggingMiddleware

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application startup", extra={"event": "app.startup"})
    yield
    logger.info("Application shutdown", extra={"event": "app.shutdown"})


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(app)
    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(v1_router, prefix=settings.api_prefix)
    app.include_router(investigation_router, prefix=settings.api_prefix)

    return app


app = create_app()
