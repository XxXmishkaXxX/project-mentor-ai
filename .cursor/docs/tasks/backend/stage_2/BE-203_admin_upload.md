# BE-203: Admin — загрузка документов

**Приоритет**: Should have
**Этап**: 2
**US**: US-12
**Зависимости**: BE-104, BE-105, BE-106, BE-103
**Статус**: не начата

## Описание

`POST /api/admin/documents` — загрузка файла администратором, пайплайн парсинга, чанкования, эмбеддинга и индексации в Qdrant.

## Файлы

- `backend/src/app/admin/schemas.py` — DTO метаданных загрузки
- `backend/src/app/admin/service.py` — сохранение файла, статусы, индексация
- `backend/src/app/admin/controller.py` — multipart endpoint, проверка роли admin

## Реализация

- Multipart: `file` (UploadFile), `title`, `description`.
- Сервис: 1) сохранить файл в `uploads/`; 2) создать запись document со `status=processing`; 3) parse + chunk + embed + upsert в Qdrant; 4) обновить `status=indexed`, `chunk_count`; 5) при ошибке — `status=error`, `error_message`.
- Доступ только для `role=admin` (middleware или dependency).

## Критерии готовности

- Загрузка PDF/DOCX/MD проходит end-to-end
- После индексации документ участвует в RAG-поиске
