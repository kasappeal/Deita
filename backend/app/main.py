"""
Main FastAPI application.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.workspaces import router as workspaces_router
from app.core.config import get_settings
from app.services.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)

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
app.include_router(auth_router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(workspaces_router, prefix="/v1/workspaces", tags=["Workspaces"])


# --- Global Exception Handlers ---
@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(status_code=404, content={"error": str(exc) or "Not found"})


@app.exception_handler(ForbiddenException)
async def forbidden_exception_handler(request: Request, exc: ForbiddenException):
    return JSONResponse(status_code=403, content={"error": str(exc) or "Forbidden"})


@app.exception_handler(BadRequestException)
async def bad_request_exception_handler(request: Request, exc: BadRequestException):
    return JSONResponse(status_code=400, content={"error": str(exc) or "Bad request"})


@app.get("/")
async def root():
    """Root endpoint redirect to docs."""
    return {
        "message": "Welcome to Deita API",
        "docs_url": "/docs",
        "api_version": "v1",
        "api_base_url": "/v1",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
