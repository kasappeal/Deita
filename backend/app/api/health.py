"""
Hello World and Health Check API routes.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas import HealthCheck, HelloWorld

router = APIRouter()
settings = get_settings()


@router.get("/", response_model=HelloWorld)
async def hello_world():
    """Hello World endpoint."""
    return HelloWorld(
        message="Hello from Deita Backend API! 🚀",
        version=settings.app_version,
        environment="development" if settings.debug else "production",
    )


@router.get("/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return HealthCheck(
        status="healthy" if db_status == "healthy" else "unhealthy",
        message=f"API is running. Database: {db_status}",
        version=settings.app_version,
        timestamp=datetime.now(UTC),
    )


@router.get("/info")
async def api_info():
    """API information endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Data exploration and AI-powered SQL assistance API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
    }
