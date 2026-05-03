import json
from datetime import datetime, timezone

from app.auth.domain.models import SessionUser
from app.base.accessor import BaseAccessor
from app.common.config import StaticConfig
from app.users.db import UserModel


class SessionAccessor(BaseAccessor):
    def _ttl_seconds(self) -> int:
        return StaticConfig.SESSION_TTL_HOURS * 3600

    async def create_session(
        self,
        session_id: str,
        user: UserModel,
    ) -> None:
        payload = {
            "user_id": str(user.id),
            "role": user.role,
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        await self.store.cache.client.set(
            key=f"{StaticConfig.SESSION_PREFIX}{session_id}",
            value=json.dumps(payload),
            expire=self._ttl_seconds(),
        )

    async def get_session(self, session_id: str) -> SessionUser | None:
        data = await self.store.cache.client.get(
            f"{StaticConfig.SESSION_PREFIX}{session_id}",
        )
        if data is None:
            return None
        return SessionUser.model_validate_json(data)

    async def delete_session(self, session_id: str) -> None:
        await self.store.cache.client.delete(
            f"{StaticConfig.SESSION_PREFIX}{session_id}",
        )
