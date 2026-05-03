from litestar.connection import Request as LitestarRequest

from app.auth.domain.models import SessionUser


class Request(LitestarRequest):
    """Application-specific request class."""

    @property
    def user(self) -> SessionUser:
        try:
            return self.state["user"]
        except KeyError:
            msg = (
                "Session data not found — "
                "is SessionMiddleware active for this route?"
            )
            raise RuntimeError(msg) from None

    @property
    def session_id(self) -> str:
        try:
            return self.state["session_id"]
        except KeyError:
            msg = (
                "Session ID not found — "
                "is SessionMiddleware active for this route?"
            )
            raise RuntimeError(msg) from None
