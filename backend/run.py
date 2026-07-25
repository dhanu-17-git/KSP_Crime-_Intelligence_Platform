import os
import sys
import uvicorn

if __name__ == "__main__":
    port_env = os.environ.get("X_ZOHO_CATALYST_LISTEN_PORT") or os.environ.get("PORT") or "9000"
    try:
        port = int(port_env)
    except ValueError:
        port = 9000
    print(f"Starting Uvicorn server on 0.0.0.0:{port}...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
