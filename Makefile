# Makefile for Deita Development

# Default target
help:
	@echo "Deita Commands:"
	@echo ""
	@echo ""
	@echo "Production:"
	@echo "  prod-up     - Start production environment"
	@echo "  prod-down   - Stop production environment"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  test        - Run all tests"
	@echo "  test-be     - Run backend tests"
	@echo "  test-fe     - Run frontend tests"
	@echo "  lint        - Run linting for all code"
	@echo "  format      - Format all code"
	@echo ""
	@echo "Database:"
	@echo "  db-migrate  - Run database migrations"
	@echo "  db-reset    - Reset database (destructive)"
	@echo "  migration	 - Generate new migration"

# Development (Dev Container)
dev:
	@echo "Opening project in VS Code dev container..."
	@echo "Make sure you have the 'Dev Containers' extension installed"
	@code .

# Production
prod-up:
	docker-compose up -d

prod-down:
	docker-compose down

# Testing (requires dev container to be running)
test: test-be test-fe

test-be:
	@echo "Running backend tests..."
	@bash -c "cd backend && uv run pytest"

test-fe:
	@echo "Running frontend tests..."
	@bash -c "cd frontend && npm test -- --watchAll=false"

# Lint all code
lint: lint-be lint-fe

lint-be:
	@echo "Linting backend with ruff..."
	@bash -c "cd backend && uv run ruff check ."

lint-fe:
	@echo "Linting frontend with eslint..."
	@bash -c "cd frontend && npm run lint"

# Format all code
format: format-be format-fe

format-be:
	@echo "Formatting backend with black and isort..."
	@bash -c "cd backend && uv run black . && uv run isort ."

format-fe:
	@echo "Formatting frontend with prettier..."
	@bash -c "cd frontend && npm run lint:fix"

# Database
db-migrate:
	@bash -c "cd backend && uv run alembic upgrade head"

db-reset:
	@bash -c "cd backend && uv run alembic downgrade base"
	@bash -c "cd backend && uv run alembic upgrade head"

# Generate migration
migration:
	@read -p "Enter migration message: " message; \
	bash -c "cd backend && uv run alembic revision --autogenerate -m \"$$message\""
