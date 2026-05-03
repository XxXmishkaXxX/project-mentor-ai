# BE-106: RAG — retriever (Qdrant)

**Приоритет**: Must have
**Этап**: 1
**US**: US-03, US-07
**Зависимости**: BE-003
**Статус**: выполнена

## Описание

Поиск релевантных чанков в Qdrant: создание коллекции, upsert точек, удаление по документу, векторный поиск с порогом скора.

## Файлы

- `backend/src/app/rag/retriever.py` — класс `Retriever`, `AsyncQdrantClient`

## Реализация

- Класс `Retriever` с `AsyncQdrantClient`.
- `ensure_collection()`: коллекция `knowledge_base`, размер вектора из конфига, расстояние Cosine.
- `upsert_chunks(document_id, chunks, vectors)`: `PointStruct`, payload `{document_id, chunk_index, content, document_title, metadata}`.
- `delete_by_document(document_id)`: удаление по фильтру.
- `search(query_vector, top_k=5, score_threshold=0.7)`: поиск и фильтрация результатов.

## Критерии готовности

- Поиск возвращает релевантные чанки со score
- Удаление по `document_id` убирает все связанные точки из Qdrant
