# Векторная БД: Qdrant

## Назначение

Хранение и поиск vector embeddings фрагментов базы знаний. Позволяет по вопросу пользователя находить наиболее похожие фрагменты документов.

## Развёртывание

Docker-контейнер:

```yaml
qdrant:
  image: qdrant/qdrant:latest
  ports:
    - "6333:6333"   # REST API
    - "6334:6334"   # gRPC
  volumes:
    - qdrant_data:/qdrant/storage
```

REST API: http://localhost:6333

Dashboard: http://localhost:6333/dashboard

## Коллекция: knowledge_base

| Параметр | Значение |
|----------|----------|
| vector size | зависит от Qwen Embedding модели (напр. 1024) |
| distance | Cosine |
| on_disk | true (экономия RAM) |

### Payload

| Поле | Тип | Назначение |
|------|-----|------------|
| document_id | string (UUID) | Связь с таблицей documents в PostgreSQL |
| chunk_index | integer | Порядковый номер фрагмента в документе |
| content | string | Полный текст фрагмента |
| document_title | string | Название документа (отображается в источниках) |
| metadata | object | Доп. метаданные: автор, тема, дата |

## Операции

### Индексация документа

При загрузке: файл -> chunking -> embedding каждого чанка -> upsert points в Qdrant

### Поиск (retrieval)

1. Embed запроса пользователя через Qwen Embedding API
2. `qdrant_client.search(collection="knowledge_base", query_vector=vector, limit=5, score_threshold=0.7)`
3. Возвращает список {document_id, document_title, content, score}

### Удаление документа

По filter: `qdrant_client.delete(collection="knowledge_base", points_selector=FilterSelector(filter=Filter(must=[FieldCondition(key="document_id", match=MatchValue(value=doc_id))])))`

### Переиндексация

Удаление старых точек по document_id + вставка новых (после повторного chunking + embedding).

## Python-клиент

Библиотека: `qdrant-client`

```python
from qdrant_client import AsyncQdrantClient

client = AsyncQdrantClient(host="localhost", port=6333)
```
