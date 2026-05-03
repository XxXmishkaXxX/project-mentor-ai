from app.common.sse import ParsedSSE, SSEEventType, parse_sse, sse_event


class TestSseEvent:
    def test_format(self):
        result = sse_event(SSEEventType.TOKEN, "hello")
        assert result == "event: token\ndata: hello\n\n"

    def test_empty_data(self):
        result = sse_event(SSEEventType.DONE, "")
        assert result == "event: done\ndata: \n\n"


class TestParseSse:
    def test_valid(self):
        raw = "event: token\ndata: hello\n\n"
        result = parse_sse(raw)
        assert result == ParsedSSE(SSEEventType.TOKEN, "hello")

    def test_missing_event(self):
        raw = "data: hello\n\n"
        assert parse_sse(raw) is None

    def test_missing_data(self):
        raw = "event: token\n\n"
        assert parse_sse(raw) is None

    def test_empty_data_parsed(self):
        """Empty data line is valid SSE — returns empty string."""
        raw = "event: done\ndata: \n\n"
        assert parse_sse(raw) == ParsedSSE(SSEEventType.DONE, "")

    def test_roundtrip(self):
        raw = sse_event(SSEEventType.SOURCES, '{"key": "value"}')
        parsed = parse_sse(raw)
        assert parsed == ParsedSSE(
            SSEEventType.SOURCES,
            '{"key": "value"}',
        )

    def test_unknown_event_returns_none(self):
        raw = "event: unknown_type\ndata: foo\n\n"
        assert parse_sse(raw) is None
