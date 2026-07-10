from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

engine_kwargs = {
    "echo": settings.database_echo,
    "pool_pre_ping": True,
}
if settings.database_url.startswith("postgresql"):
    engine_kwargs["pool_size"] = settings.database_pool_size
    engine_kwargs["max_overflow"] = settings.database_max_overflow

engine = create_async_engine(
    settings.database_url,
    **engine_kwargs,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
