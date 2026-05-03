from cashews import Cache, cache

from app.base.accessor import BaseAccessor
from app.store.cache.config import CacheConfig


class CacheAccessor(BaseAccessor):
    async def connect(self) -> None:
        config = CacheConfig.from_settings(self.store.settings.config)
        cache.setup(f"redis://{config.host}:{config.port}")

    async def disconnect(self) -> None:
        await cache.close()

    @property
    def client(self) -> Cache:
        return cache
