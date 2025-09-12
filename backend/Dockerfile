# Backend Dockerfile - Multi-stage build for development and production
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set work directory
WORKDIR /app

# Development stage
FROM base as development

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies including dev dependencies
RUN uv sync --dev

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r deita && useradd -r -g deita deita
RUN chown -R deita:deita /app
USER deita

# Expose port
EXPOSE 8000

# Run development server with auto-reload
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install only production dependencies
RUN uv sync --no-dev

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r deita && useradd -r -g deita deita
RUN chown -R deita:deita /app
USER deita

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run production server
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
