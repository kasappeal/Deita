"""
Core configuration and settings for Deita backend application.
"""

from functools import lru_cache

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration."""

    # === Application Settings ===
    app_name: str = Field(default="Deita", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # === Database Configuration ===
    database_url: str = Field(
        default="postgresql://deita:password@localhost:5432/deita_dev",
        alias="DATABASE_URL",
    )

    # === DuckDB Configuration ===
    duckdb_path: str = Field(default="/app/data/analytics.duckdb", alias="DUCKDB_PATH")

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
    max_file_size: int = Field(default=209715200, alias="MAX_FILE_SIZE")
    max_workspace_storage: int = Field(
        default=1073741824, alias="MAX_WORKSPACE_STORAGE"
    )

    # === Analytics (Posthog) ===
    posthog_enabled: bool = Field(default=False, alias="POSTHOG_ENABLED")
    posthog_api_key: str | None = Field(default=None, alias="POSTHOG_API_KEY")
    posthog_host: str = Field(default="https://app.posthog.com", alias="POSTHOG_HOST")

    # === AI Service Configuration ===
    ai_model_name: str = Field(default="local-llm", alias="AI_MODEL_NAME")
    ai_model_endpoint: str = Field(
        default="http://localhost:8001", alias="AI_MODEL_ENDPOINT"
    )
    ai_model_api_key: str | None = Field(default=None, alias="AI_MODEL_API_KEY")

    # === CORS ===
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="ALLOWED_ORIGINS",
    )

    @validator("allowed_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
