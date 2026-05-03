from app.common.sse import parse_sse, sse_event


class TestSseEvent:
    def test_format(self):
        result = sse_event("token", "hello")
        assert result == "event: token\ndata: hello\n\n"

    def test_empty_data(self):
        result = sse_event("done", "")
        assert result == "event: done\ndata: \n\n"


class TestParseSse:
    def test_valid(self):
        raw = "event: token\ndata: hello\n\n"
        result = parse_sse(raw)
        assert result == ("token", "hello")

    def test_missing_event(self):
        raw = "data: hello\n\n"
        assert parse_sse(raw) is None

    def test_missing_data(self):
        raw = "event: token\n\n"
        assert parse_sse(raw) is None

    def test_empty_data_returns_none(self):
        """Empty data after strip() loses trailing space → unparseable."""
        raw = "event: done\ndata: \n\n"
        assert parse_sse(raw) is None

    def test_roundtrip(self):
        original_event = "sources"
        original_data = '{"key": "value"}'
        raw = sse_event(original_event, original_data)
        parsed = parse_sse(raw)
        assert parsed == (original_event, original_data)
