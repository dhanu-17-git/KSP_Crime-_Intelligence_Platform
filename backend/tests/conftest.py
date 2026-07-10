import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def test_environment() -> None:
    os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
    os.environ.setdefault("ENVIRONMENT", "test")


@pytest.fixture
def client() -> TestClient:
    from app.main import app

    return TestClient(app)
