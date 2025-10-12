# Stage 1: Build stage with dependencies and build tools
FROM python:3.12-slim AS build

# Set environment variables for build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies and build tools
RUN apt-get update && \
    apt-get install -y build-essential curl wget && \
    rm -rf /var/lib/apt/lists/* && \
    pip install uv

# Copy dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies including dev dependencies for build
RUN uv sync

# Copy source code
COPY . .

# Stage 2: Production stage with minimal runtime dependencies
FROM python:3.12-slim AS production

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && \
    apt-get install -y curl libmagic1 && \
    rm -rf /var/lib/apt/lists/* && \
    pip install uv && \
    groupadd -r deita && \
    useradd -r -g deita deita

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install only production dependencies
RUN uv sync --no-dev

# Copy application code from build stage
COPY --from=build /app/app ./app
COPY --from=build /app/migrations ./migrations
COPY --from=build /app/alembic.ini ./

# Set proper ownership
RUN chown -R deita:deita /app

# Switch to non-root user
USER deita

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run production server
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
