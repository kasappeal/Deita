# Deita - Data Exploration and AI-Powered Analysis Platform

Deita is a web-based platform that empowers small business owners and students to extract, explore, and analyze data from CSV files without requiring advanced technical skills. The platform combines intuitive data exploration with AI-powered SQL generation and natural language explanations through a conversational chat interface.

## 🌟 Motivation: Building Software with AI Superpowers 🤖🦾

Deita isn’t just another data platform — it’s a bold experiment in what happens when you let AI drive the entire software development journey. The mission? To learn, push boundaries, and see how far you can go when you apply AI tools to every stage of building a real product — from idea, plan, architecture and design, to coding, testing, and docs.

Here’s the cool part: Over 80% of the work behind Deita was powered by AI, and a whopping 90% of the code was written by AI (using both, agents and assistant). Human creativity set the vision, but AI did the heavy lifting—proving that the future of software is collaborative, fast, and a little bit magical.

## 🚀 Key Features

### Core Functionality

- **📁 Drag-and-drop file upload** for CSV files (Excel support planned)
- **📊 Interactive data exploration** with tabular views and pagination
- **🤖 AI-powered SQL generation** from natural language questions via chat interface
- **💬 Persistent chat history** for conversational AI interactions
- **📝 Query management** - Save, load, and delete SQL queries
- **📤 Export capabilities** - Stream query results as CSV files
- **🔐 Magic link authentication** for seamless, password-free sign-in
- **👥 Workspace management** with public/private visibility control
- **🔄 Real-time query execution** with DuckDB analytics engine

### User Experience

- **Anonymous access** - Start using immediately without sign-up
- **Orphan workspaces** - Automatic workspace creation for anonymous users
- **Workspace claiming** - Registered users can claim anonymous workspaces
- **Storage limits** - 50MB/100MB for orphan, 200MB/200MB for owned workspaces
- **Automatic cleanup** - Inactive workspaces deleted after retention period (15/30 days)
- **Email notifications** - Warning emails before deletion, confirmation after

## 🏗️ Architecture

Deita follows a modern, scalable architecture with clear separation of concerns:

- **Backend**: FastAPI (Python) with Clean Architecture patterns
- **Frontend**: React 18 with TypeScript and Chakra UI
- **Database**: PostgreSQL for metadata, DuckDB for analytics
- **Storage**: S3-compatible object storage (MinIO in dev, S3 in prod)
- **AI**: LiteLLM client with OpenRouter for multi-model support
- **Authentication**: JWT-based magic link email authentication
- **Rate Limiting**: SlowAPI middleware (100 req/min default)

### Architecture Diagram

```
┌─────────────┐      HTTPS       ┌──────────────┐
│   Browser   │ ◄──────────────► │   Frontend   │
│             │                  │  (React SPA) │
└─────────────┘                  └──────┬───────┘
                                        │ API Calls
                                        │ /v1/*
                                 ┌──────▼───────┐
                                 │   Backend    │
                                 │   (FastAPI)  │
                                 └──────┬───────┘
                    ┌───────────────┬───┴─┬───────────────┐
                    │               │     │               │
              ┌─────▼─────┐   ┌─────▼──┐  │          ┌────▼────┐
              │PostgreSQL │   │ DuckDB │  │          │ MinIO/S3│
              │(Metadata) │   │(OLAP)  │  │          │(Files)  │
              └───────────┘   └────────┘  │          └─────────┘
                                      ┌───▼──────┐
                                      │LiteLLM/  │
                                      │OpenRouter│
                                      └──────────┘
```

## 🛠️ Technology Stack

### Backend

- **Framework**: FastAPI (Python 3.11+)
- **Package Manager**: uv (fast Python package management)
- **Databases**:
  - PostgreSQL (SQLAlchemy, Alembic migrations)
  - DuckDB (analytical queries)
- **Storage**: boto3 (S3-compatible)
- **AI**: LiteLLM (OpenRouter integration)
- **Auth**: python-jose (JWT), Passlib (bcrypt)
- **Rate Limiting**: SlowAPI
- **Validation**: Pydantic, sqlglot
- **Testing**: Pytest, pytest-cov
- **Linting**: Ruff

### Frontend

- **Framework**: React 18 with TypeScript
- **UI Library**: Chakra UI 2 with Emotion
- **Build Tool**: Vite
- **State Management**: React Context API, Zustand
- **Router**: React Router DOM
- **HTTP Client**: Axios
- **Testing**: Jest, React Testing Library
- **Linting**: ESLint, Prettier

### Infrastructure

- **Development**: Docker Compose, MinIO, MailHog
- **CI/CD**: GitHub Actions

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Quick Start with VS Code Dev Container (Recommended)

1. **Clone the repository**

```bash
git clone https://github.com/kasappeal/deita.git
cd deita
```

2. **Open in VS Code Dev Container**

   - Open the project in VS Code: `code .`
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Run "Dev Containers: Reopen in Container"
   - Wait for the container to build and all services to start

3. **Start development servers**

In the dev container terminal:

```bash
# Terminal 1: Start backend
cd backend
uv run fastapi dev --host=0.0.0.0 --port=8000

# Terminal 2: Start frontend (new terminal)
cd frontend
npm start
```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MailHog: http://localhost:8025

### Manual Setup (Without Dev Container)

1. **Install prerequisites**

   - Python 3.11+ with [uv](https://github.com/astral-sh/uv)
   - Node.js 18+
   - Docker & Docker Compose

2. **Install dependencies**

```bash
# Backend
cd backend
uv sync

# Frontend
cd ../frontend
npm install
```

3. **Start supporting services**

```bash
docker-compose -f docker-compose.dev.yml up -d
```

4. **Run migrations**

```bash
cd backend
uv run alembic upgrade head
```

5. **Start development servers** (same as dev container step 3)

### Environment Configuration

Copy example environment files and update as needed:

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env.local
```

Key environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`: Object storage config
- `SMTP_HOST`, `SMTP_PORT`: Email service config
- `AI_MODEL_API_KEY`: OpenRouter API key for AI features
- `SECRET_KEY`: JWT signing key (change in production!)

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- [System Architecture](docs/01-system-architecture.md) - Overall system design and components
- [Technology Stack](docs/02-technology-stack.md) - Detailed technology choices and rationale
- [Data Model Design](docs/03-data-model-design.md) - Database schema and relationships
- [API Design](docs/04-api-design.md) - Complete REST API reference
- [Service Boundaries](docs/05-service-boundaries.md) - Service layer organization
- [Performance & Scalability](docs/06-performance-scalability.md) - Performance considerations
- [Security](docs/07-security.md) - Security practices and compliance
- [Development Best Practices](docs/08-development-best-practices.md) - Coding standards
- [Deployment Best Practices](docs/09-deployment-best-practices.md) - Production deployment
- [Risk Assessment](docs/10-risk-assessment-technical-debt.md) - Technical debt and risks
- [Development Environment](docs/11-dev-environment.md) - Dev setup guide

### API Documentation

- **Interactive API Docs**: http://localhost:8000/docs (when running)
- **ReDoc**: http://localhost:8000/redoc (alternative API docs)

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest app/tests/test_auth_endpoints.py
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

## 📝 Development Commands

### Backend

```bash
# Format and lint
uv run ruff check .
uv run ruff format .

# Create migration
uv run alembic revision --autogenerate -m "description"

# Run migrations
uv run alembic upgrade head

# Reset database (destructive)
uv run alembic downgrade base
uv run alembic upgrade head
```

### Frontend

```bash
# Lint
npm run lint

# Fix linting issues
npm run lint:fix

# Type check
npm run type-check

# Build for production
npm run build
```

## 🚢 Deployment

### Production Build

```bash
# Build and start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Production Checklist

- [ ] Change `SECRET_KEY` in backend/.env
- [ ] Configure proper CORS origins
- [ ] Set up HTTPS/TLS certificates
- [ ] Configure production SMTP service
- [ ] Update S3 credentials for production storage
- [ ] Set `DEBUG=false` in backend configuration
- [ ] Configure proper rate limiting thresholds
- [ ] Set up monitoring and alerting
- [ ] Review and apply security best practices

## 📊 Project Status

### ✅ Implemented Features

- Magic link authentication with JWT
- Workspace CRUD with public/private visibility
- CSV file upload with S3 storage
- SQL query execution with DuckDB
- Query management (save/load/delete)
- AI-powered SQL generation via chat
- Chat message persistence and history
- CSV export with streaming
- Rate limiting and CORS protection
- Comprehensive test coverage

### 🚧 In Progress / Planned

- Excel file support (multi-sheet handling)
- Table renaming functionality
- Natural language result explanations
- Relationship suggestions between tables
- Automatic workspace deletion (cleanup job)
- Query sharing capabilities
- Enhanced monitoring and analytics
- Responsive design

**Current Version**: 0.1.0 (Alpha)

## 🆘 Support

- 📖 Check the [documentation](docs/) for detailed information
- 🐛 Report bugs via [GitHub Issues](https://github.com/kasappeal/deita/issues)

----

Built with ❤️ by Alberto Casero
