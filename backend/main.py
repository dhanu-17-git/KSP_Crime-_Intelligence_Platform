import os
import uvicorn
from app.main import app

__all__ = ["app"]

if __name__ == "__main__":
    port_env = os.environ.get("PORT", "8000")
    port = int(port_env)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
