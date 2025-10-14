# Deita Development Environment Documentation

## Overview

This document describes how to set up and use the Deita development environment. The development setup uses VS Code Dev Containers for a "one-click setup" experience, providing developers with a fully configured environment to work on both backend and frontend components.

## Architecture

The development environment consists of:

- **Dev Container** (optional): A single container with all development tools (Python, Node.js, uv, npm)
- **PostgreSQL**: Primary database for metadata
- **MinIO**: S3-compatible object storage for file uploads (development only)
- **MailHog**: Email testing service for magic link authentication (development only)
- **DuckDB**: Analytical database (file-based, shared volume)

## Prerequisites

- **Docker** (with Docker Compose)
- **VS Code** with the "Dev Containers" extension
- **Git**

## Quick Start (Recommended: Dev Container)

### 1. Clone the Repository

```bash
git clone https://github.com/kasappeal/deita.git
cd deita
```

### 2. Open in VS Code Dev Container

**Option A: VS Code Command Palette**

1. Open the project in VS Code: `code .`
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Run "Dev Containers: Reopen in Container"
4. Wait for the container to build and all services to start

**Option B: Manual Python & Node Setup + Docker Compose**

1. **Install prerequisites:**

   - Python 3.12+ (recommended: use [uv](https://github.com/astral-sh/uv) for Python package management)
   - Node.js 22+
   - Docker & Docker Compose

2. **Install backend dependencies:**

   ```bash
   cd backend
   uv sync
   # Or: pip install -r requirements.txt (if not using uv)
   cd ..
   ```

3. **Install frontend dependencies:**

   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Start supporting services (PostgreSQL, MinIO, MailHog):**

   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

### 3. Start Development Servers

Once the dev container or supporting services are running

# Terminal 1: Start backend

```bash
cd backend
uv run fastapi dev --host=0.0.0.0 --port=8000
```

# Terminal 2: Start frontend (open new terminal)

```bash
cd frontend
npm start
```

## Project Structure

```
deita/
├── .devcontainer/ # VS Code dev container configuration
│ ├── devcontainer.json # Dev container settings
│ └── docker-compose.dev.yml # Dev container services
├── backend/ # FastAPI Python backend
│ ├── app/
│ │ ├── api/ # REST API endpoints
│ │ ├── core/ # Configuration and database
│ │ ├── models/ # SQLAlchemy models
│ │ ├── services/ # Business logic
│ │ │ └── ai/ # AI functionality
│ │ ├── utils/ # Utility functions
│ │ └── tests/ # Test suite
│ ├── migrations/ # Alembic database migrations
│ ├── pyproject.toml # Python dependencies and tool config
│ └── Dockerfile # Backend container definition
│ ├── src/
│ │ ├── components/ # React components by feature
│ │ ├── hooks/ # Custom React hooks
│ │ ├── types/ # TypeScript definitions
│ │ ├── utils/ # Helper functions
│ │ ├── contexts/ # React context providers
│ │ └── pages/ # Top-level page components
│ ├── package.json # Node.js dependencies
├── docker-compose.yml # Production environment
└── Makefile # Development commands
```

### Frontend Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if needed)
npm install

# Run tests
npm test

# Lint and format code
npm run lint
npm run lint:fix

# Type checking
npm run type-check

# Start development server
npm run dev
```

### Database Management

```bash
# Run migrations
make db-migrate

# Reset database (destructive)
make db-reset

# Generate new migration
make migration
```

## Testing

### Running Tests

```bash
# All tests
make test

# Backend tests only
make test-be

# Frontend tests only
make test-fe
```

### Test Structure

- **Backend**: Uses pytest with fixtures and test data
- **Frontend**: Uses Jest and React Testing Library
- **Integration**: End-to-end tests with Playwright (planned)

## Code Quality

### Linting and Formatting

```bash
# Lint all code
make lint

# Format all code
make format
```

### Pre-configured Tools

- **Backend**: Ruff
- **Frontend**: ESLint, Prettier, TypeScript
- **VS Code**: Extensions and settings automatically configured

## Debugging

### VS Code Debugging

The dev container comes with debugging pre-configured:

1. **Backend**: Python debugger with FastAPI support
2. **Frontend**: Chrome DevTools integration
3. **Breakpoints**: Set breakpoints in VS Code for both Python and TypeScript

## Environment Variables

### Backend (`backend/.env`)

| Variable                    | Description                  | Example Value                                |
| --------------------------- | ---------------------------- | -------------------------------------------- |
| DATABASE_URL                | PostgreSQL connection string | postgresql://deita:deita@postgres:5432/deita |
| S3_ENDPOINT                 | MinIO/S3 endpoint            | http://minio:9000                            |
| S3_ACCESS_KEY               | MinIO/S3 access key          | deita                                        |
| S3_SECRET_KEY               | MinIO/S3 secret key          | deita123                                     |
| S3_BUCKET_NAME              | MinIO/S3 bucket name         | deita-files                                  |
| SMTP_HOST                   | Email server host            | mailhog                                      |
| SMTP_PORT                   | Email server port            | 1025                                         |
| SMTP_USER                   | Email server username        | (blank for dev)                              |
| SMTP_PASSWORD               | Email server password        | (blank for dev)                              |
| FROM_EMAIL                  | Default sender email         | noreply@deita.app                            |
| SECRET_KEY                  | App secret key               | your-secret-key-here-change-in-production    |
| ALGORITHM                   | JWT algorithm                | HS256                                        |
| ACCESS_TOKEN_EXPIRE_MINUTES | JWT token expiry (minutes)   | 43200                                        |
| ENVIRONMENT                 | Environment name             | development                                  |
| DEBUG                       | Debug mode                   | true                                         |
| APP_NAME                    | Application name             | Deita                                        |
| APP_VERSION                 | Application version          | 0.1.0                                        |
| DUCKDB_PATH                 | DuckDB file path             | /app/data/deita.duckdb                       |
| AI_MODEL_NAME               | AI model name                | local-llm                                    |
| AI_MODEL_ENDPOINT           | AI model endpoint            | http://localhost:8001                        |
| AI_MODEL_API_KEY            | AI model API key             | (blank for dev)                              |

### Frontend (`frontend/.env.local`)

| Variable         | Description          | Example Value            |
| ---------------- | -------------------- | ------------------------ |
| VITE_API_URL     | Backend API base URL | http://localhost:8000/v1 |
| VITE_ENVIRONMENT | Environment name     | development              |
| VITE_APP_NAME    | Application name     | Deita                    |

## Production Deployment

The production environment uses optimized containers:

```bash
# Build and start production
make prod-up

# Stop production
make prod-down
```
