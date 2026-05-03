import os
from pathlib import Path
from typing import Any

import yaml


class FileLoader:
    def __init__(self, path: str) -> None:
        self.path = path

    def load(self) -> dict[str, Any]:
        p = Path(self.path)
        if not p.exists():
            return {}
        with p.open() as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}

    def __repr__(self) -> str:
        return f"FileLoader({self.path!r})"


class EnvLoader:
    """Loads config from env vars with ``APP_`` prefix.

    Nested keys use double-underscore as separator:
    ``APP_DB__HOST=localhost`` → ``{"db": {"host": "localhost"}}``
    """

    PREFIX = "APP_"

    def load(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in os.environ.items():
            if not key.startswith(self.PREFIX):
                continue
            parts = key[len(self.PREFIX) :].lower().split("__")
            d = result
            for part in parts[:-1]:
                d = d.setdefault(part, {})
            d[parts[-1]] = value
        return result


class OneOfLoader:
    """Returns config from the first loader that yields a non-empty dict."""

    def __init__(self, loaders: list[FileLoader]) -> None:
        self.loaders = loaders

    def load(self) -> dict[str, Any]:
        for loader in self.loaders:
            data = loader.load()
            if data:
                return data
        return {}


def deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def path(config: dict, *keys: str, default: Any = None) -> Any:
    """Safely traverse a nested dict by a sequence of keys."""
    d: Any = config
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key, default)
        if d is default:
            return default
    return d


class Settings:
    def __init__(
        self,
        loaders: list[FileLoader | EnvLoader | OneOfLoader],
        debug: bool | None = None,
        use_uvloop: bool = True,
    ) -> None:
        self.loaders = loaders
        self.debug = debug or False
        self.use_uvloop = use_uvloop
        self.config: dict[str, Any] = {}

    def load_config(self) -> None:
        config: dict[str, Any] = {}
        for loader in self.loaders:
            data = loader.load()
            config = deep_merge(config, data)
        self.config = config
