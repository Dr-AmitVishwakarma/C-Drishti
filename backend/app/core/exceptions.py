import logging

from fastapi import Request
from fastapi.exceptions import (
    RequestValidationError,
)
from fastapi.responses import (
    JSONResponse,
)
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,
)


logger = logging.getLogger(
    "c_drishti.errors"
)


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    """
    Handle standard HTTP exceptions consistently.
    """

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "status_code": (
                    exc.status_code
                ),
                "message": exc.detail,
                "path": request.url.path,
            }
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """
    Handle request validation failures.
    """

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "type": (
                    "validation_error"
                ),
                "status_code": 422,
                "message": (
                    "Request validation failed."
                ),
                "path": request.url.path,
                "details": exc.errors(),
            }
        },
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Handle unexpected server errors without exposing
    internal implementation details to API consumers.
    """

    logger.exception(
        "Unhandled exception "
        "method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": (
                    "internal_server_error"
                ),
                "status_code": 500,
                "message": (
                    "An unexpected server "
                    "error occurred."
                ),
                "path": request.url.path,
            }
        },
    )