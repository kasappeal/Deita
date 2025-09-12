# Copilot Instructions for Deita Codebase

## Project Overview

- **Deita** is a web platform for data exploration and AI-powered SQL analysis, targeting non-technical users.
- **Architecture:**
  - **Frontend:** React (TypeScript, Chakra UI) in `frontend/`
  - **Backend:** FastAPI (Python) in `backend/` using Clean Architecture
  - **Databases:** PostgreSQL (metadata), DuckDB (analytics)
  - **Storage:** S3-compatible (MinIO for dev)
  - **AI:** In-house service for SQL generation/explanation

## Key Workflows

- **Backend (FastAPI):**
  - Entry: `backend/app/main.py` (mounts routers, configures CORS, etc.)
  - Config: `backend/app/core/config.py` (env vars, DB, S3, etc.)
  - API routes: `backend/app/api/` (e.g., `health.py` for health/healt)
  - Models/Schemas: `backend/app/models/`, `backend/app/schemas/`
  - DB: SQLAlchemy models, Alembic migrations (`backend/migrations/`)
  - **Dev commands:**
    - Install deps: `uv sync`
    - Run server: `uv fastapi dev --host=0.0.0.0 --port=8000`
    - Migrate DB: `uv run alembic upgrade head`
    - Create migration: `uv run alembic revision --autogenerate -m "msg"`
    - Lint: `uv run ruff check .`
- **Frontend (React):**
  - Entry: `frontend/src/main.tsx`, main app: `frontend/src/App.tsx`
  - Components: `frontend/src/components/`
  - API: `frontend/src/services/api.ts`
  - **Dev commands:**
    - Start dev: `npm run dev` (in `frontend/`)
    - Build: `npm run build`
    - Test: `npm run test`
    - Lint: `npm run lint`

## Patterns & Conventions

- **Backend:**
  - Clean separation: `api/`, `core/`, `models/`, `schemas/`, `services/`, `utils/`
  - Use Pydantic for validation, SQLAlchemy for DB, Alembic for migrations
  - All config via env vars (see `.env.example`)
  - API versioning: `/v1/`
- **Frontend:**
  - React Query for server state, Chakra UI for styling
  - TypeScript everywhere, strict typing
  - API calls abstracted in `services/api.ts`
  - Tests in `src/__tests__/`

## Integration Points

- **Frontend ↔ Backend:** REST API (see `docs/04-api-design.md`)
- **Backend ↔ DB:** SQLAlchemy ORM, DuckDB for analytics
- **Backend ↔ S3:** MinIO in dev, S3 in prod (see config)
- **Backend ↔ AI:** Internal service for SQL generation/explanation

## References

- [System Architecture](../docs/01-system-architecture.md)
- [API Design](../docs/04-api-design.md)
- [Data Model](../docs/03-data-model-design.md)
- [Dev Environment](../docs/11-dev-environment.md)

---

**For AI agents:**

- Always follow the Clean Architecture boundaries in backend.
- Use provided scripts/commands for builds, tests, and migrations.
- Reference the docs for API/data model details before making cross-component changes.
- Prefer updating config via env vars, not hardcoding.
- Use versioned API routes (`/v1/`).
- Keep code modular and type-safe (TypeScript/Pydantic).
