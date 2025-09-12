# Deita Backend

FastAPI backend for the Deita data exploration platform.

### Development Setup

1. **Set up environment variables**:

```bash
cp .env.example .env
# Edit .env with your database credentials
```

2. **Install dependencies**:

```bash
uv sync
```

3. **Run database migrations**:

```bash
uv run alembic upgrade head
```

4. **Start the development server**:

```bash
uv fastapi dev --host=0.0.0.0 --port=8000
```

The API will be available at:

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/v1/health
- **Hello World**: http://localhost:8000/v1/

## Environment Variables

Read [Dev Enviroment docs](../docs/11-dev-environment.md)

## API Endpoints

Read [API Design docs](../docs/04-api-design.md)

## Database

### Migrations

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

View migration history:

```bash
uv run alembic history
```

## Testing

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=app
```

## Code Quality

Lint code:

```bash
uv run ruff check .
```
