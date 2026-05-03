def sse_event(event: str, data: str) -> str:
    data_lines = "\n".join(f"data: {line}" for line in data.split("\n"))
    return f"event: {event}\n{data_lines}\n\n"


def parse_sse(raw: str) -> tuple[str, str] | None:
    event_type = None
    data_parts: list[str] = []
    for line in raw.strip().splitlines():
        if line.startswith("event: "):
            event_type = line[7:]
        elif line.startswith("data: "):
            data_parts.append(line[6:])
        elif line == "data:":
            data_parts.append("")
    if event_type is not None and data_parts:
        return event_type, "\n".join(data_parts)
    return None
