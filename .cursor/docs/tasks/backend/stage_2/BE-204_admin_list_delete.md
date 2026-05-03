# BE-204: Admin — список и удаление документов

**Приоритет**: Should have
**Этап**: 2
**US**: US-12
**Зависимости**: BE-203
**Статус**: не начата

## Описание

`GET /api/admin/documents` и `DELETE /api/admin/documents/{doc_id}` — управление индексом для администратора.

## Файлы

- `backend/src/app/admin/controller.py` — list и delete маршруты
- `backend/src/app/admin/service.py` — пагинация, каскадное удаление из PG, Qdrant и ФС

## Реализация

- `GET`: список документов с `offset`, `limit`, сортировка `created_at` DESC.
- `DELETE`: удалить строку в PG, удалить точки в Qdrant по `document_id`, удалить файл с диска.
- Только роль `admin`.

## Критерии готовности

- Список с пагинацией корректен
- После DELETE документ отсутствует в PG, чанки убраны из Qdrant, файл удалён
- Не-admin получает отказ в доступе
