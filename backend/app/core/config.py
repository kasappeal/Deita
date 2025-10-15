"""
Core configuration and settings for Deita backend application.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and configuration."""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    # === Application Settings ===
    app_name: str = Field(default="Deita", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    api_rate_limit: str = Field(default="100/minute", alias="API_RATE_LIMIT")

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # === Database Configuration ===
    database_url: str = Field(
        default="postgresql://deita:password@localhost:5432/deita_dev",
        alias="DATABASE_URL",
    )
    database_pool_size: int = Field(default=10, alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=5, alias="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, alias="DATABASE_POOL_TIMEOUT")
    database_pool_recycle: int = Field(default=300, alias="DATABASE_POOL_RECYCLE")

    # === DuckDB Configuration ===
    duckdb_path: str = Field(default="/app/data/analytics.duckdb", alias="DUCKDB_PATH")
    duckdb_page_size: int = Field(default=50, alias="DUCKDB_PAGE_SIZE")

    # === Object Storage (MinIO/S3) ===
    s3_endpoint: str = Field(default="http://minio:9000", alias="S3_ENDPOINT")
    s3_access_key: str = Field(default="deita", alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="deita123", alias="S3_SECRET_KEY")
    s3_bucket_name: str = Field(default="deita-files", alias="S3_BUCKET_NAME")

    # === Email Configuration ===
    smtp_host: str = Field(default="localhost", alias="SMTP_HOST")
    smtp_port: int = Field(default=1025, alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    from_email: str = Field(default="noreply@deita.app", alias="FROM_EMAIL")

    # === Security ===
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production", alias="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=43200, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # === File Upload Limits ===
    orphaned_workspace_max_file_size: int = Field(default=52428800, alias="ORPHANED_WORKSPACE_MAX_FILE_SIZE")
    orphaned_workspace_max_storage: int = Field(default=104857600, alias="ORPHANED_WORKSPACE_MAX_STORAGE")
    owned_workspace_max_file_size: int = Field(default=209715200, alias="OWNED_WORKSPACE_MAX_FILE_SIZE")
    owned_workspace_max_storage: int = Field(default=209715200, alias="OWNED_WORKSPACE_MAX_STORAGE")

    # === AI Service Configuration ===
    ai_model_name: str = Field(default="local-llm", alias="AI_MODEL_NAME")
    ai_model_endpoint: str = Field(
        default="http://localhost:8001", alias="AI_MODEL_ENDPOINT"
    )
    ai_model_api_key: str | None = Field(default=None, alias="AI_MODEL_API_KEY")

    # === CORS ===
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["*"],
        alias="ALLOWED_ORIGINS",
    )

    # === Allowed hosts ===
    allowed_hosts: list[str] = Field(
        default_factory=lambda: ["*"],
        alias="ALLOWED_HOSTS",
    )

    # === Frontend Configuration ===
    frontend_url: str = Field(
        default="http://localhost:3000", alias="FRONTEND_URL"
    )

    # === Query timeout ===
    query_timeout_seconds: int = Field(default=30, alias="QUERY_TIMEOUT_SECONDS")

    # === Workspace Cleanup Configuration ===
    # Retention periods in days
    orphaned_workspace_retention_days: int = Field(
        default=15, alias="ORPHANED_WORKSPACE_RETENTION_DAYS"
    )
    owned_workspace_retention_days: int = Field(
        default=30, alias="OWNED_WORKSPACE_RETENTION_DAYS"
    )

    # Warning intervals in days (before deletion)
    workspace_warning_intervals: list[int] = Field(
        default_factory=lambda: [15, 10, 5, 3, 1],
        alias="WORKSPACE_WARNING_INTERVALS"
    )

    # Cleanup job schedule (cron expression: run daily at 2 AM)
    cleanup_job_cron: str = Field(
        default="0 2 * * *", alias="CLEANUP_JOB_CRON"
    )

    # Enable/disable cleanup job
    cleanup_job_enabled: bool = Field(
        default=True, alias="CLEANUP_JOB_ENABLED"
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()

