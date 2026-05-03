# BE-107: RAG — LLM клиент

**Приоритет**: Must have
**Этап**: 1
**US**: US-03
**Зависимости**: BE-003
**Статус**: выполнена

## Описание

Асинхронный клиент Qwen 3.6 API в формате, совместимом с OpenAI: потоковая генерация ответа (SSE).

## Файлы

- `backend/src/app/rag/llm.py` — класс `LLMClient`, стриминг чанков текста

## Реализация

- Класс `LLMClient` с `httpx.AsyncClient`.
- `stream_completion(messages: list[dict]) -> AsyncGenerator[str, None]`: `POST` на `{QWEN_API_BASE_URL}/chat/completions`, `model=QWEN_MODEL`, `stream=True`.
- Разбор SSE: строки `data: {...}`; извлечение `choices[0].delta.content`.
- Обработка ошибок API и таймаутов.

## Критерии готовности

- Стриминг отдаёт токены/фрагменты по мере прихода
- Ошибки и таймауты не роняют процесс без явной обработки; пользователь/лог получают понятный сигнал
