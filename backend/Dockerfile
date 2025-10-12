FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Copy application code
COPY . .

# Install system dependencies
RUN apt-get install -y build-essential curl wget libmagic1  && \
     rm -rf /var/lib/apt/lists/*                            && \
     pip install uv                                         && \
     uv sync --no-dev                                       && \
     groupadd -r deita                                      && \
     useradd -r -g deita deita                              && \
     chown -R deita:deita /app                              && \

USER deita

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run production server
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
