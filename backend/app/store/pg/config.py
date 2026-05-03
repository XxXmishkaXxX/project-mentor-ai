from dataclasses import dataclass
from urllib.parse import quote_plus

from app.global_.settings import path


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    name: str = "mentor_ai"
    user: str = "postgres"
    password: str = "postgres"  # noqa: S105

    @property
    def url(self) -> str:
        user = quote_plus(self.user)
        password = quote_plus(self.password)
        return (
            f"postgresql+asyncpg://{user}:{password}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    @classmethod
    def from_settings(cls, config: dict) -> "DatabaseConfig":
        return cls(
            host=path(
                config,
                "store",
                "database",
                "host",
                default="localhost",
            ),
            port=int(
                path(config, "store", "database", "port", default=5432),
            ),
            name=path(
                config,
                "store",
                "database",
                "name",
                default="mentor_ai",
            ),
            user=path(
                config,
                "store",
                "database",
                "user",
                default="postgres",
            ),
            password=path(
                config,
                "store",
                "database",
                "password",
                default="postgres",
            ),
        )
