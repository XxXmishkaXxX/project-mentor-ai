# BE-105: RAG — embedder

**Приоритет**: Must have
**Этап**: 1
**US**: US-03
**Зависимости**: BE-003
**Статус**: выполнена

## Описание

HTTP-клиент для Qwen Embedding API: получение векторных представлений для одного текста и батча.

## Файлы

- `backend/src/app/rag/embedder.py` — класс `Embedder`, вызовы embeddings API

## Реализация

- Класс `Embedder` с `httpx.AsyncClient`.
- `embed_text(text) -> list[float]`: `POST` на `{QWEN_API_BASE_URL}/embeddings`, `model=QWEN_EMBEDDING_MODEL`.
- `embed_batch(texts) -> list[list[float]]`: батч-запрос.
- Обработка rate limit, повторных попыток (retries), таймаутов.

## Критерии готовности

- `embed_text("Что такое Scrum?")` возвращает вектор ожидаемой размерности
- `embed_batch([...])` обрабатывает список текстов
