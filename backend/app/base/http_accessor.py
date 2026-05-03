import asyncio
from typing import Any

import httpx

from app.base.accessor import BaseAccessor
from app.common.config import StaticConfig


class BaseHttpAccessor(BaseAccessor):
    """Base class for accessors that communicate with external HTTP APIs."""

    def _build_timeout(self) -> httpx.Timeout | float:
        return StaticConfig.EMBEDDER_TIMEOUT

    def _build_headers(self, api_key: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def _init_client(
        self,
        base_url: str,
        api_key: str,
        timeout: httpx.Timeout | float | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=self._build_headers(api_key),
            timeout=timeout or self._build_timeout(),
        )

    async def disconnect(self) -> None:
        if hasattr(self, "_client"):
            await self._client.aclose()

    async def _request(
        self,
        path: str,
        method: str = "POST",
        **kwargs: Any,
    ) -> httpx.Response:
        last_exc: Exception | None = None

        for attempt in range(1, StaticConfig.HTTP_MAX_RETRIES + 1):
            try:
                resp = await self._client.request(method, path, **kwargs)

                if resp.status_code in StaticConfig.HTTP_RETRY_CODES:
                    self.logger.warning(
                        "retryable status, retrying",
                        status=resp.status_code,
                        attempt=attempt,
                    )
                    await resp.aclose()
                    await asyncio.sleep(
                        StaticConfig.HTTP_BASE_RETRY_DELAY
                        * (2 ** (attempt - 1)),
                    )
                    continue

                resp.raise_for_status()
                return resp

            except httpx.TimeoutException as exc:
                self.logger.warning(
                    "request timeout, retrying",
                    attempt=attempt,
                )
                last_exc = exc
                await asyncio.sleep(
                    StaticConfig.HTTP_BASE_RETRY_DELAY * (2 ** (attempt - 1)),
                )
            except httpx.HTTPStatusError as exc:
                self.logger.error(
                    "HTTP error",
                    status=exc.response.status_code,
                    body=exc.response.text,
                )
                raise

        msg = f"{type(self).__name__} failed after {StaticConfig.HTTP_MAX_RETRIES} retries"
        raise RuntimeError(msg) from last_exc

    async def _request_json(
        self,
        path: str,
        method: str = "POST",
        **kwargs: Any,
    ) -> dict:
        resp = await self._request(path, method, **kwargs)
        return resp.json()

    async def _open_stream(
        self,
        path: str,
        method: str = "POST",
        **kwargs: Any,
    ) -> httpx.Response:
        """Open a streaming connection with retries."""
        last_exc: Exception | None = None

        for attempt in range(1, StaticConfig.HTTP_MAX_RETRIES + 1):
            try:
                req = self._client.build_request(method, path, **kwargs)
                resp = await self._client.send(req, stream=True)

                if resp.status_code in StaticConfig.HTTP_RETRY_CODES:
                    self.logger.warning(
                        "stream retryable status, retrying",
                        status=resp.status_code,
                        attempt=attempt,
                    )
                    await resp.aclose()
                    await asyncio.sleep(
                        StaticConfig.HTTP_BASE_RETRY_DELAY
                        * (2 ** (attempt - 1)),
                    )
                    continue

                resp.raise_for_status()
                return resp

            except httpx.TimeoutException as exc:
                self.logger.warning(
                    "stream timeout, retrying",
                    attempt=attempt,
                )
                last_exc = exc
                await asyncio.sleep(
                    StaticConfig.HTTP_BASE_RETRY_DELAY * (2 ** (attempt - 1)),
                )
            except httpx.HTTPStatusError as exc:
                try:
                    await exc.response.aread()
                    body = exc.response.text
                except Exception:
                    body = "<could not read response body>"
                self.logger.error(
                    "stream HTTP error",
                    status=exc.response.status_code,
                    body=body,
                )
                raise

        msg = f"{type(self).__name__} stream failed after {StaticConfig.HTTP_MAX_RETRIES} retries"
        raise RuntimeError(msg) from last_exc
