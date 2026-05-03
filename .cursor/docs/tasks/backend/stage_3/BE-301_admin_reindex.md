# BE-301: Admin — переиндексация документа

**Приоритет**: Could have
**Этап**: 3
**US**: US-13
**Зависимости**: BE-203
**Статус**: не начата

## Описание

`POST /api/admin/documents/{doc_id}/reindex` — полное обновление векторного представления документа без смены файла на диске.

## Файлы

- `backend/src/app/admin/controller.py` — endpoint reindex
- `backend/src/app/admin/service.py` — удаление старых точек, повторный parse/chunk/embed/upsert

## Реализация

- Удалить старые чанки в Qdrant по `document_id`.
- Заново прочитать файл с диска по `file_path`, parse → chunk → embed → upsert.
- Обновить `chunk_count`, `status` (и при ошибке — `error_message`).

## Критерии готовности

- После reindex поиск возвращает актуальное содержимое документа
- Метаданные документа в PG согласованы с количеством чанков
