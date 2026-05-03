from dataclasses import dataclass

from app.global_.settings import path


@dataclass
class CacheConfig:
    host: str = "localhost"
    port: int = 6379

    @classmethod
    def from_settings(cls, config: dict) -> "CacheConfig":
        return cls(
            host=path(
                config,
                "store",
                "cache",
                "host",
                default="localhost",
            ),
            port=int(
                path(config, "store", "cache", "port", default=6379),
            ),
        )
