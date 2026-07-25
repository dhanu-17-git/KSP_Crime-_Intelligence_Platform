import os
import uvicorn
from app.main import app

__all__ = ["app"]

if __name__ == "__main__":
    port_env = os.environ.get("X_ZOHO_CATALYST_LISTEN_PORT") or os.environ.get("PORT") or "8000"
    port = int(port_env)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
