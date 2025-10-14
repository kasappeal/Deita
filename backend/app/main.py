"""
Main FastAPI application.
"""

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

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

# Add SlowAPI rate limiting middleware
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add trusted host middleware (security)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

# Include routers
app.include_router(health_router, prefix="/v1", tags=["Health"])
app.include_router(auth_router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(workspaces_router, prefix="/v1/workspaces", tags=["Workspaces"])

# Apply global rate limit to all endpoints (default: 100 requests/minute per IP)
# Apply rate limiting to all routers using dependencies
def limit_dependency(request: Request):
    return limiter.limit(settings.api_rate_limit)(lambda: None)(request)

for router in [health_router, auth_router, workspaces_router]:
    router.dependencies = [Depends(limit_dependency)] + getattr(router, 'dependencies', [])


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


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Convert HTTPException detail to error for consistency."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
        headers=exc.headers
    )


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
