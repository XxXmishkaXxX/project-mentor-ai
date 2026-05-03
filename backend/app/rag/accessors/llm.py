import json
from collections.abc import AsyncGenerator

import httpx

from app.base.http_accessor import BaseHttpAccessor
from app.common.config import StaticConfig
from app.rag.config import QwenConfig


class LLMAccessor(BaseHttpAccessor):
    async def connect(self) -> None:
        config = QwenConfig.from_settings(self.store.settings.config)
        self._config = config
        await self._init_client(
            base_url=config.api_base_url,
            api_key=config.api_key,
            timeout=httpx.Timeout(
                connect=StaticConfig.LLM_CONNECT_TIMEOUT,
                read=StaticConfig.LLM_STREAM_TIMEOUT,
                write=StaticConfig.LLM_CONNECT_TIMEOUT,
                pool=StaticConfig.LLM_CONNECT_TIMEOUT,
            ),
        )
        self.logger.info("llm connected", model=config.model)

    async def stream_completion(
        self,
        messages: list[dict[str, str]],
    ) -> AsyncGenerator[str, None]:
        payload = {
            "model": self._config.model,
            "messages": messages,
            "stream": True,
        }

        resp = await self._open_stream(
            "POST", "/chat/completions", json=payload
        )
        try:
            async for line in resp.aiter_lines():
                token = _parse_sse_line(line)
                if token is not None:
                    yield token
        finally:
            await resp.aclose()


def _parse_sse_line(line: str) -> str | None:
    """Extract content delta from an SSE data line."""
    line = line.strip()
    if not line.startswith("data: "):
        return None

    data = line[len("data: ") :]
    if data == "[DONE]":
        return None

    try:
        obj = json.loads(data)
        choices = obj.get("choices", [])
        if not choices:
            return None
        delta = choices[0].get("delta", {})
        return delta.get("content")
    except (json.JSONDecodeError, KeyError, IndexError):
        return None
