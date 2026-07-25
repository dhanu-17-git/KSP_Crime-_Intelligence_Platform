FROM python:3.13-slim AS base

# ── Security: run as non-root user ─────────────────────────────────────
RUN groupadd -r kspapi && useradd -r -g kspapi kspapi

# ── Build environment ───────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ── Install deps separately for Docker layer cache efficiency ───────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ───────────────────────────────────────────────
COPY . .

# ── Drop privileges ─────────────────────────────────────────────────────
USER kspapi

EXPOSE 8000

# ── Health check ────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2", "--log-config", "logging_config.json"]
