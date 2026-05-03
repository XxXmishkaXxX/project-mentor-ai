import os
from contextvars import ContextVar
from dataclasses import dataclass

from app.global_.settings import Settings


def _read_version() -> str:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    version_path = os.path.join(current_dir, "..", "VERSION")
    if not os.path.exists(version_path):
        return "dev"
    with open(version_path) as f:
        return f.read().strip()


@dataclass(frozen=True)
class AppInfo:
    name: str
    version: str


global_settings: ContextVar[Settings] = ContextVar("global_settings")
app_info = AppInfo(
    name="project-mentor-ai",
    version=_read_version(),
)
