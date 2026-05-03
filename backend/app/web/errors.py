import structlog
from litestar import Request, Response
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
from litestar.types import Scope

log = structlog.get_logger("web.errors")


async def after_exception_handler(exc: Exception, scope: Scope) -> None:
    path = scope.get("path", "unknown")
    method = scope.get("method", "unknown")

    if isinstance(exc, HTTPException) and exc.status_code < 500:
        log.warning(
            "HTTP error",
            status=exc.status_code,
            detail=exc.detail,
            method=method,
            path=path,
        )
        return

    log.exception(
        "Unhandled exception",
        method=method,
        path=path,
        exc_info=exc,
    )


def internal_server_error_handler(
    _request: Request,
    exc: Exception,
) -> Response:
    log.exception("Internal server error", exc_info=exc)
    return Response(
        content={"detail": "Internal server error"},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )
