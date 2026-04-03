"""
AEGISCORE — FastAPI Application Entry Point
Self-Hosted AI Security Intelligence Platform

Author: Mohamed Adhnaan J M
Brand: BYTEAEGIS
Website: byteaegis.in
GitHub: BYTEGUARDIAN14
Registration: 6176AC23UCS097
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("aegiscore")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    logger.info("AEGISCORE %s starting up...", settings.APP_VERSION)
    # Database initialized via Alembic locally or CI
    logger.info("Proceeding to application startup")
    yield
    logger.info("AEGISCORE shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Self-Hosted AI Security Intelligence Platform. "
        "Multi-repo scanning, ML risk forecasting, AI-powered fixes, "
        "cross-repo correlation. Zero data egress."
    ),
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── CORS Middleware ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ───────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return a clean 500 response."""
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__,
        },
    )


# ── Register Routers ───────────────────────────────────────────────────────
from routers.auth import router as auth_router
from routers.orgs import router as orgs_router
from routers.repos import router as repos_router
from routers.scans import router as scans_router
from routers.findings import router as findings_router
from routers.risk import router as risk_router
from routers.fixes import router as fixes_router
from routers.correlations import router as correlations_router
from routers.metrics import router as metrics_router

API_PREFIX = settings.API_V1_PREFIX

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(orgs_router, prefix=API_PREFIX)
app.include_router(repos_router, prefix=API_PREFIX)
app.include_router(scans_router, prefix=API_PREFIX)
app.include_router(findings_router, prefix=API_PREFIX)
app.include_router(risk_router, prefix=API_PREFIX)
app.include_router(fixes_router, prefix=API_PREFIX)
app.include_router(correlations_router, prefix=API_PREFIX)
app.include_router(metrics_router, prefix=API_PREFIX)


# ── Health Check ────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/api/v1/health", tags=["Health"])
async def api_health_check():
    """API-level health check with component status."""
    components = {
        "api": "healthy",
        "database": "unknown",
        "redis": "unknown",
    }

    # Check database connectivity
    try:
        from database import AsyncSessionLocal
        from sqlalchemy import text

        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            components["database"] = "healthy"
    except Exception as e:
        components["database"] = f"unhealthy: {str(e)[:100]}"

    # Check Redis connectivity
    try:
        import redis as redis_lib

        r = redis_lib.from_url(settings.REDIS_URL, decode_responses=True)
        r.ping()
        components["redis"] = "healthy"
        r.close()
    except Exception as e:
        components["redis"] = f"unhealthy: {str(e)[:100]}"

    overall = "healthy" if all(
        v == "healthy" for v in components.values()
    ) else "degraded"

    return {
        "status": overall,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "components": components,
    }
