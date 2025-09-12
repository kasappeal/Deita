"""
Main FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.health import router as health_router
from app.api.workspace import router as workspace_router
from app.core.config import get_settings

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Data exploration and AI-powered SQL assistance platform",
    openapi_url="/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware (security)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # Configure this properly in production
)

# Include routers
app.include_router(health_router, prefix="/v1", tags=["Health"])
app.include_router(workspace_router, prefix="/v1", tags=["Workspaces"])


@app.get("/")
async def root():
    """Root endpoint redirect to docs."""
    return {
        "message": "Welcome to Deita API",
        "docs_url": "/docs",
        "api_version": "v1",
        "api_base_url": "/v1",
    }


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    print(f"🚀 {settings.app_name} v{settings.app_version} starting up...")
    print("📚 API Documentation: /docs")
    print("🏥 Health Check: /v1/health")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    print(f"👋 {settings.app_name} shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
