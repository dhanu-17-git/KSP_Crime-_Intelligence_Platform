import os
import asyncio
import pytest
from fastapi.testclient import TestClient

# Ensure test isolation before any app module or settings are imported
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["AI_PROVIDER"] = "none"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    from app.seed import create_tables, seed_database
    from app.database.database import engine, Base

    async def _init_models():
        await create_tables()
        await seed_database()

    asyncio.run(_init_models())
    yield
    async def _drop_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
    try:
        asyncio.run(_drop_models())
    except Exception:
        pass
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except Exception:
            pass


@pytest.fixture
def client() -> TestClient:
    from app.main import app

    return TestClient(app)
