from dataclasses import dataclass
from enum import StrEnum


class SSEEventType(StrEnum):
    TOKEN = "token"  # noqa: S105
    ERROR = "error"
    SOURCES = "sources"
    DONE = "done"
    NO_DATA = "no_data"


@dataclass(frozen=True, slots=True)
class ParsedSSE:
    event: SSEEventType
    data: str


def sse_event(event: SSEEventType, data: str) -> str:
    data_lines = "\n".join(f"data: {line}" for line in data.split("\n"))
    return f"event: {event}\n{data_lines}\n\n"


def parse_sse(raw: str) -> ParsedSSE | None:
    event_type = None
    data_parts: list[str] = []
    for line in raw.strip().splitlines():
        if line.startswith("event: "):
            event_type = line[7:]
        elif line.startswith("data: "):
            data_parts.append(line[6:])
        elif line == "data:":
            data_parts.append("")
    if event_type is None or not data_parts:
        return None
    try:
        return ParsedSSE(
            event=SSEEventType(event_type),
            data="\n".join(data_parts),
        )
    except ValueError:
        return None
