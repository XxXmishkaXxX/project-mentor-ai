def sse_event(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"


def parse_sse(raw: str) -> tuple[str, str] | None:
    event_type = None
    data = None
    for line in raw.strip().splitlines():
        if line.startswith("event: "):
            event_type = line[7:]
        elif line.startswith("data: "):
            data = line[6:]
    if event_type is not None and data is not None:
        return event_type, data
    return None
