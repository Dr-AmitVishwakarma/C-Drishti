from fastapi import FastAPI
from fastapi.exceptions import (
    RequestValidationError,
)
from fastapi.middleware.cors import (
    CORSMiddleware,
)
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,
)

from app.api.analytics import (
    router as analytics_router,
)
from app.api.health import (
    router as health_router,
)
from app.api.rag import (
    router as rag_router,
)
from app.api.system import (
    router as system_router,
)
from app.core.config import settings
from app.core.exceptions import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging_config import (
    configure_logging,
)
from app.core.middleware import (
    RequestLoggingMiddleware,
)


configure_logging()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Backend API for C-Drishti, "
        "an AI-assisted integrated "
        "enforcement intelligence and "
        "decision-support platform."
    ),
    debug=settings.debug,
)


app.add_middleware(
    RequestLoggingMiddleware
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_origin,
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    unhandled_exception_handler,
)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": (
            settings.environment
        ),
        "status": "running",
        "documentation": "/docs",
    }


app.include_router(
    health_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    system_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    analytics_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    rag_router,
    prefix=settings.api_v1_prefix,
)