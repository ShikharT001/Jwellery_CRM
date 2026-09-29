"""
FastAPI application factory.

This file creates the FastAPI application, registers middleware,
mounts routers, and sets up global exception handlers.

The application is created once and imported by the ASGI server (uvicorn).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import configure_logging, get_logger
from app.db.session import check_database_connection
from app.modules.auth.router import router as auth_router
from app.modules.organizations.router import router as organizations_router
from app.modules.subscriptions.router import router as subscriptions_router
from app.modules.roles.router import router as roles_router
from app.modules.audit.router import router as audit_router
from app.modules.inventory.router import router as inventory_router
from app.shared.schemas import ErrorResponse, HealthResponse

# Configure logging before anything else
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.

    Code before yield: runs on startup
    Code after yield: runs on shutdown
    """
    logger.info(
        "Starting Jewellery ERP API",
        environment=settings.environment,
        debug=settings.debug,
    )

    # Verify database connection on startup
    if check_database_connection():
        logger.info("Database connection: OK")
    else:
        logger.error("Database connection: FAILED — check DATABASE_URL")

    yield

    logger.info("Shutting down Jewellery ERP API")


def create_application() -> FastAPI:
    """
    Application factory — creates and configures the FastAPI instance.

    Using a factory function (instead of a module-level app variable)
    makes it easier to create test instances with different configurations.
    """
    app = FastAPI(
        title="Jewellery ERP SaaS API",
        description="Multi-tenant Jewellery ERP platform API",
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ─────────────────────────────────────────────
    # CORS Middleware
    # ─────────────────────────────────────────────
    # Allow the Next.js frontend to make requests to this API.
    # In production, CORS_ORIGINS should be set to your actual domain.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Organization-ID"],
        expose_headers=["X-Request-ID"],
    )

    # ─────────────────────────────────────────────
    # Global Exception Handlers
    # ─────────────────────────────────────────────
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """
        Handle all custom AppException subclasses uniformly.
        Returns a consistent JSON error response.
        """
        logger.warning(
            "Application error",
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                success=False,
                error_code=exc.error_code,
                message=exc.message,
                details=exc.details,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions — log and return 500."""
        logger.exception(
            "Unhandled exception",
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred. Please try again later.",
            ).model_dump(),
        )

    # ─────────────────────────────────────────────
    # Health Check Endpoint
    # ─────────────────────────────────────────────
    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["System"],
        summary="Health check",
    )
    def health_check():
        """
        Returns the current health status of the API.

        Used by deployment platforms (Railway, Render) to verify
        the application is running correctly.
        """
        db_ok = check_database_connection()
        return HealthResponse(
            status="ok" if db_ok else "degraded",
            database="connected" if db_ok else "disconnected",
            version="1.0.0",
            environment=settings.environment,
        )

    # ─────────────────────────────────────────────
    # Register Routers
    # ─────────────────────────────────────────────
    api_prefix = settings.api_v1_prefix

    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(organizations_router, prefix=api_prefix)
    app.include_router(subscriptions_router, prefix=api_prefix)
    app.include_router(roles_router, prefix=api_prefix)
    app.include_router(audit_router, prefix=api_prefix)
    app.include_router(inventory_router, prefix=api_prefix)

    return app


# The ASGI application instance
# uvicorn imports this: `uvicorn app.main:app`
app = create_application()
