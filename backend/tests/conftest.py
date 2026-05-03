import os
import warnings

import pytest

os.environ.setdefault("DISABLE_UVLOOP", "1")

from app.global_.settings import EnvLoader, FileLoader, Settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    config_path = os.environ.get("CONFIG", "tests/config.yaml")
    s = Settings(
        loaders=[
            FileLoader(config_path),
            EnvLoader(),
        ],
        debug=False,
        use_uvloop=False,
    )
    s.load_config()
    return s


@pytest.fixture(autouse=True, scope="session")
def _load_global_settings(settings: Settings) -> None:
    from app import global_settings

    global_settings.set(settings)


@pytest.fixture(scope="session")
def event_loop():
    import asyncio

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=ResourceWarning)

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
