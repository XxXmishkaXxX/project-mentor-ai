from litestar.connection import Request

from app.auth.domain.models import SessionUser


class AppRequest(Request):
    @property
    def user(self) -> SessionUser:
        return self.state["user"]

    @property
    def session_id(self) -> str:
        return self.state["session_id"]
