import json

from litestar.connection import Request
from litestar.types import ASGIApp, Receive, Scope, Send

from app import global_store
from app.common.config import StaticConfig

WHITELIST_PATHS: frozenset[str] = frozenset(
    {
        "/api/auth/login",
        "/api/auth/register",
        "/api/health",
    }
)

WHITELIST_PREFIXES: tuple[str, ...] = (
    "/docs",
    "/schema",
)


class SessionMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        req_path = scope["path"]
        if req_path in WHITELIST_PATHS or req_path.startswith(
            WHITELIST_PREFIXES
        ):
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        session_id = request.cookies.get(
            StaticConfig.SESSION_COOKIE_NAME,
        )
        if not session_id:
            await self._send_401(send)
            return

        store = global_store.get()
        session_data = await store.session_accessor.get_session(session_id)
        if not session_data:
            await self._send_401(send)
            return

        scope.setdefault("state", {})
        scope["state"]["user"] = session_data
        scope["state"]["session_id"] = session_id
        await self.app(scope, receive, send)

    @staticmethod
    async def _send_401(send: Send) -> None:
        body = json.dumps({"detail": "Not authenticated"}).encode()
        await send(
            {
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"content-length", str(len(body)).encode()],
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": body,
            }
        )
