from app.base.http_accessor import BaseHttpAccessor
from app.common.config import StaticConfig
from app.rag.config import QwenConfig


class EmbedderAccessor(BaseHttpAccessor):
    async def connect(self) -> None:
        config = QwenConfig.from_settings(self.store.settings.config)
        self._config = config
        await self._init_client(
            base_url=config.api_base_url,
            api_key=config.api_key,
            timeout=StaticConfig.EMBEDDER_TIMEOUT,
        )
        self.logger.info(
            "embedder connected",
            model=config.embedding_model,
        )

    async def embed_text(self, text: str) -> list[float]:
        data = await self._embed_request([text])
        return data[0]

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        batch_size = StaticConfig.EMBEDDING_MAX_BATCH_SIZE
        if len(texts) <= batch_size:
            return await self._embed_request(texts)

        results: list[list[float]] = []
        for offset in range(0, len(texts), batch_size):
            batch = texts[offset : offset + batch_size]
            results.extend(await self._embed_request(batch))
        return results

    async def _embed_request(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        payload = {
            "model": self._config.embedding_model,
            "input": texts,
        }
        body = await self._request_json("POST", "/embeddings", json=payload)
        return [
            item["embedding"]
            for item in sorted(body["data"], key=lambda x: x["index"])
        ]
