import os
from functools import lru_cache

# Load values from the local .env file if present, respecting active environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
if os.environ.get("ENVIRONMENT") != "test" and os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, val = line.strip().split("=", 1)
                k = key.strip()
                if k not in os.environ:
                    os.environ[k] = val.strip().strip('"').strip("'")

from app.core.settings import Settings


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings loaded from the environment."""
    return Settings()
