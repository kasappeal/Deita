FROM python:3.12-slim

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Copy dependency files 
COPY . /app

# Install only runtime system dependencies
RUN apt-get update && \
    apt-get install -y curl libmagic1 && \
    rm -rf /var/lib/apt/lists/* && \
    pip install uv && \
    groupadd -r deita && \
    useradd -r -g deita deita  && \
    uv sync --no-dev   && \
    mkdir -p /home/deita/.cache/uv && \
    chown -R deita:deita /app /home/deita/.cache/uv

# Switch to non-root user
USER deita

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run production server
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
