<div align="center">



# KSP Crime Intelligence Platform

### AI-Powered Investigation & Command Intelligence System

**Karnataka State Police Datathon 2026 — Problem Statement 1**


[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/react-19-61DAFB.svg)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115-009688.svg)](https://fastapi.tiangolo.com)



---

> **Demo Credentials** — `Username: IPS001` · `Password: demo123`

</div>

---

## Overview

The KSP Crime Intelligence Platform is a full-stack, AI-powered law enforcement investigation assistant built for the Karnataka State Police Datathon 2026. It transforms natural-language officer queries into structured, multi-source intelligence dossiers — cross-referencing FIR databases, ANPR vehicle logs, suspect biometric profiles, and CDR records in real time.

**Core design principle:** Free natural-language input → formal, authoritative intelligence output. Not a chatbot. Not a CRUD system. An agentic investigation engine.

---

## Screenshots

| Dashboard — Command Center | AI Investigation Workspace |
|:-:|:-:|
| Live KPI metrics, GIS crime map, active incident feed | Multi-source dossier pipeline with Gemini AI analysis |

| Suspect Intel Registry | Criminal Network Graph |
|:-:|:-:|
| Risk-scored profiles with gang affiliations | Interactive D3-style syndicate link visualization |

---

## Key Features

### 🤖 AI Investigation Engine
- **Natural Language Queries** — Officers type freely; AI extracts entities, retrieves evidence, and generates formal intelligence reports
- **Multi-Stage Pipeline** — Entity Extraction → FIR/ANPR/CDR Retrieval → Relationship Analysis → Gemini AI Report Generation
- **Agentic Console** — Direct command interface: notify police stations, flag suspects, log case notes via conversational commands
- **Thread-Aware Conversations** — Follow-up queries build on prior context using server-side thread management

### 🗄️ Intelligence Data Sources
- **FIR Database** — Case master records, crime categories, severity classifications
- **Suspect Registry** — Biometric profiles, gang affiliations, risk scores, arrest history
- **ANPR Vehicle Logs** — License plate scans, camera locations, ownership cross-references
- **Criminal Network Graph** — Visualized syndicate link maps with relationship type tagging

### 🗺️ Operational Modules
- **Live Crime Map** — GIS-based Leaflet incident heatmap for Bengaluru
- **Analytics Dashboard** — Crime trend charts, district-wise breakdowns, temporal patterns
- **Formal Report Generator** — Printable, classified investigation dossiers
- **Bilingual Interface** — Full English + Kannada (ಕನ್ನಡ) language support

### 🔒 Security & Access Control
- **JWT Authentication** — Stateless token-based auth with role-based access
- **Officer-Grade UI** — Classified information banners, access-level indicators
- **Law Enforcement Tone** — AI responses maintain formal, professional police intelligence language

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    KSP Crime Intelligence Platform                  │
├────────────────────────┬────────────────────────────────────────────┤
│    Frontend (React)    │           Backend (FastAPI)                │
│                        │                                            │
│  ┌──────────────────┐  │  ┌──────────────────────────────────────┐ │
│  │  AI Workspace    │  │  │  Investigation Engine                │ │
│  │  - Quick Dossier │◄─┼──│  ┌──────────────┐  ┌─────────────┐ │ │
│  │  - Agentic Chat  │  │  │  │ Entity       │  │ Retrieval   │ │ │
│  └──────────────────┘  │  │  │ Extractor    │→ │ Provider    │ │ │
│  ┌──────────────────┐  │  │  └──────────────┘  └─────────────┘ │ │
│  │  Dashboard       │  │  │  ┌──────────────┐  ┌─────────────┐ │ │
│  │  Crime Map       │  │  │  │ Gemini AI    │  │ PostgreSQL  │ │ │
│  │  Suspect Registry│  │  │  │ Provider     │  │ (Neon)      │ │ │
│  │  Vehicle Logs    │  │  │  └──────────────┘  └─────────────┘ │ │
│  │  Network Graph   │  │  └──────────────────────────────────────┘ │
│  └──────────────────┘  │                                            │
│                        │  ┌──────────────────────────────────────┐ │
│  Vite + React 19       │  │  REST API — /api/v1                  │ │
│  TypeScript            │  │  /investigation/query  (thread-aware) │ │
│  Tailwind CSS v4       │  │  /auth/login, /auth/me               │ │
│  React Router v7       │  │  /health                             │ │
│  Leaflet Maps          │  └──────────────────────────────────────┘ │
│  ECharts               │                                            │
│  React Flow            │  FastAPI + SQLAlchemy (async)             │
└────────────────────────┴────────────────────────────────────────────┘
                         │
            ┌────────────┴──────────────┐
            │   Zoho Catalyst           │
            │   Web Client (dist/)      │
            │   AppSail (backend/)      │
            └───────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Frontend Framework** | React + TypeScript | 19.x + 6.x |
| **Build Tool** | Vite | 8.x |
| **Styling** | Tailwind CSS | 4.x |
| **Routing** | React Router (Hash mode) | 7.x |
| **Maps** | Leaflet.js | 1.x |
| **Charts** | Apache ECharts | 6.x |
| **Network Graphs** | React Flow (@xyflow) | 12.x |
| **Backend Framework** | FastAPI | 0.115.x |
| **Runtime** | Python | 3.13 |
| **ASGI Server** | Uvicorn | 0.34.x |
| **ORM** | SQLAlchemy (async) | 2.0.x |
| **Database Driver** | asyncpg | 0.30.x |
| **Database** | PostgreSQL (Neon serverless) | — |
| **AI Provider** | Google Gemini API | gemini-flash-latest |
| **Auth** | JWT (python-jose) | — |
| **Migrations** | Alembic | 1.14.x |
| **Testing** | pytest + pytest-asyncio | 8.x |
| **Deployment** | Zoho Catalyst (AppSail + Web Client) | — |
| **CI/CD** | GitHub Actions | — |

---

## Project Structure

```
DATATHON-2026/
├── .github/
│   └── workflows/
│       ├── ci.yml          # Test + build on every push/PR
│       ├── cd.yml          # Deploy to Zoho Catalyst on main merge
│       └── security.yml    # Weekly dependency vulnerability scan
│
├── src/                    # React frontend
│   ├── pages/
│   │   ├── AIWorkspace/    # Core AI Investigation module
│   │   ├── Dashboard/      # Command center with KPIs + copilot
│   │   ├── Suspects/       # Biometric risk-scored suspect registry
│   │   ├── Vehicles/       # ANPR vehicle watchlist
│   │   ├── CriminalNetwork/# Interactive syndicate link graph
│   │   ├── CrimeMap/       # GIS Leaflet heatmap
│   │   ├── Analytics/      # Crime trend charts
│   │   ├── Cases/          # FIR case browser
│   │   └── Reports/        # Report management
│   ├── services/
│   │   ├── investigationApi.ts   # Backend API calls
│   │   └── mockDb.ts             # Demo data (fallback)
│   ├── context/
│   │   └── AppContext.tsx         # Global state (auth, queries, language)
│   └── components/
│       └── ui/MapWidget.tsx       # Reusable Leaflet map wrapper
│
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── investigation.py  # Main AI pipeline endpoint
│   │   │   ├── auth.py           # JWT auth endpoints
│   │   │   └── health.py         # Health check
│   │   ├── investigation/
│   │   │   ├── engine.py         # 4-stage investigation orchestrator
│   │   │   ├── providers/
│   │   │   │   └── gemini.py     # Gemini AI provider + tools
│   │   │   ├── entity_extraction.py
│   │   │   └── retrieval.py      # PostgreSQL retrieval provider
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── core/
│   │   │   ├── settings.py       # Pydantic settings
│   │   │   └── database.py       # Async engine setup
│   │   └── middleware/
│   │       └── request_logging.py
│   ├── alembic/            # Database migrations
│   ├── tests/              # pytest test suite
│   ├── Dockerfile          # Production container
│   ├── requirements.txt
│   └── main.py             # ASGI entry point
│
├── catalyst.json           # Zoho Catalyst deploy config
├── vite.config.ts
├── package.json
└── README.md
```

---

## Getting Started

### Prerequisites

| Tool | Minimum Version |
|------|----------------|
| Node.js | 20+ |
| Python | 3.11+ |
| PostgreSQL | 14+ (or Neon account) |
| Google Gemini API key | Free tier sufficient |

---

### 1 — Clone the Repository

```bash
git clone https://github.com/dhanu-17-git/DATATHON-2026.git
cd DATATHON-2026
```

---

### 2 — Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Edit `backend/.env` with your values:

```env
# Database — use Neon serverless or local PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@host/ksp_crime_intel?ssl=require

# JWT — generate a strong random secret
JWT_SECRET_KEY=your-very-long-random-secret-key-here

# Google Gemini AI
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL_NAME=gemini-1.5-flash

# App
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:5173"]
```

```bash
# Run database migrations
alembic upgrade head

# Seed demo data (officers, suspects, FIRs)
python run.py seed

# Start backend server
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

API is now live at **`http://127.0.0.1:8000`** · Interactive docs at **`/docs`**

---

### 3 — Frontend Setup

```bash
# From project root
npm install

# Start development server
npm run dev
```

Frontend is now live at **`http://localhost:5173`**

> **Login:** `IPS001` / `demo123`

---

### 4 — Verify Everything Works

```bash
# Health check
curl http://127.0.0.1:8000/api/v1/health

# Expected: {"status": "healthy", "database": "connected", "version": "0.1.0"}
```

---

## CI/CD Pipeline

The project uses a **two-workflow GitHub Actions pipeline** with full separation between integration and deployment concerns.

### Workflow Overview

```
Push to any branch ──► ci.yml (Test & Build)
                           │
                           ├─ backend-tests     Python pytest, coverage report
                           ├─ frontend-build    oxlint + TypeScript + Vite build
                           └─ docker-smoke-test Docker build + container health check

Push to main ────────► cd.yml (Deploy to Catalyst)
                           │
                           ├─ pre-deploy-checks  Determine targets (all / frontend / backend)
                           ├─ deploy-frontend     Vite build → Catalyst Web Client
                           ├─ deploy-backend      FastAPI → Catalyst AppSail
                           └─ notify-deployment   GitHub Step Summary report
```

### Required GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|--------|-------------|
| `CATALYST_AUTH_TOKEN` | Zoho Catalyst CLI auth token |
| `CATALYST_PROJECT_ID` | Zoho Catalyst project ID |
| `VITE_API_BASE_URL` | Production backend URL for frontend build |

### Manual Deployment

Use **workflow_dispatch** to deploy selectively from the GitHub Actions UI:

- **`all`** — deploy both frontend and backend
- **`frontend-only`** — rebuild and push web client only  
- **`backend-only`** — redeploy AppSail service only

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | `development` / `production` / `test` |
| `DATABASE_URL` | — | PostgreSQL asyncpg connection string |
| `JWT_SECRET_KEY` | — | **Required.** Long random secret for JWT signing |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token lifetime in minutes |
| `AI_PROVIDER` | `none` | `gemini` or `none` (disables AI, uses fallbacks) |
| `GEMINI_API_KEY` | `""` | Google Gemini API key |
| `GEMINI_MODEL_NAME` | `gemini-1.5-pro` | Gemini model identifier |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed frontend origins (JSON array) |
| `LOG_LEVEL` | `INFO` | Python log level |

### Frontend (Vite env)

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend base URL (e.g. `https://api.example.com/api/v1`) |

---

## API Reference

Base URL: `/api/v1`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/login` | — | Officer login, returns JWT |
| `GET` | `/auth/me` | ✅ JWT | Current officer profile |
| `GET` | `/health` | — | Service health check |
| `POST` | `/investigation/query` | ✅ JWT | Main AI investigation pipeline |
| `POST` | `/investigation/followup` | ✅ JWT | Legacy follow-up (use `/query` with `thread_id`) |
| `GET` | `/firs/` | ✅ JWT | List FIR records |
| `GET` | `/suspects/` | ✅ JWT | List suspect profiles |
| `GET` | `/vehicles/` | ✅ JWT | List ANPR vehicle records |

### Investigation Query Request

```json
POST /api/v1/investigation/query
Authorization: Bearer <token>

{
  "query_text": "Find all suspects connected with vehicle KA05MJ4421",
  "requested_by": "IPS001",
  "thread_id": null,
  "is_follow_up": false,
  "conversation_history": []
}
```

### Investigation Query Response

```json
{
  "report_text": "Based on ANPR records, vehicle KA05MJ4421...",
  "thread_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "type": "report",
  "is_follow_up": false,
  "entities_found": ["KA05MJ4421"],
  "evidence_count": 7,
  "risk_score": 82
}
```

---

## Running Tests

```bash
cd backend

# Run full test suite
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov-report=term-missing

# Run specific test module
pytest tests/test_investigation_engine.py -v

# Run with parallel workers (faster)
pip install pytest-xdist
pytest tests/ -n auto
```

---

## Deployment — Zoho Catalyst

### Manual Deploy

```bash
# Install Catalyst CLI
npm install -g zcatalyst-cli

# Login to Catalyst
catalyst login

# Full deploy (frontend + backend)
catalyst deploy

# Frontend only
catalyst deploy --only web-client

# Backend (AppSail) only
catalyst deploy --only appsail
```

### Live Endpoints

| Component | URL |
|-----------|-----|
| 🌐 Web Application | https://ksp-datathon-2026-60079582909.development.catalystserverless.in/app/index.html |
| ⚙️ API Backend | https://ksp-crime-intel-api-50044310157.development.catalystappsail.in |
| 📋 API Swagger Docs | https://ksp-crime-intel-api-50044310157.development.catalystappsail.in/docs |

---

## Contributing

This project was built for a competitive datathon. For reference, the full product specification is in [KSP_AI_Investigation_Build_Spec.md](KSP_AI_Investigation_Build_Spec.md).

### Development Workflow

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes, then commit
git add .
git commit -m "feat: describe your change"

# Push and open a pull request
git push origin feature/your-feature-name
```

### Commit Convention

| Prefix | Usage |
|--------|-------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `chore:` | Build, CI, deps |
| `docs:` | Documentation |
| `refactor:` | Code restructure |
| `test:` | Test additions |

---

## Known Limitations

- **Gemini API Rate Limits** — The free tier (60 RPM) can cause temporary 429 errors under load. The backend automatically falls back to deterministic responses when Gemini is throttled.
- **In-Memory Thread Store** — Investigation threads are stored in-memory on the backend process. Threads are lost on AppSail service restarts. Production deployment should use Redis for thread persistence.
- **Demo Data** — The Suspects, Vehicles, and Network Graph pages use mock data from `src/services/mockDb.ts`. Live integration with the PostgreSQL FIR/Accused tables is implemented in the AI pipeline only.

---

## License

[MIT License](LICENSE) — Karnataka State Police Datathon 2026 submission.

---

<div align="center">

Built for the **Karnataka State Police Datathon 2026**

**Problem Statement 1 — AI-Powered Investigation Intelligence Platform**

</div>
