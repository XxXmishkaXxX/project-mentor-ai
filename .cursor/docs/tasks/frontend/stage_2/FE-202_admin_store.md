# FE-202: Admin Store (Pinia)

**Приоритет**: Should have
**Этап**: 2
**US**: US-12
**Зависимости**: BE-203, BE-204
**Статус**: не начата

## Описание

Состояние админ-раздела для базы знаний: список документов, флаг загрузки файла. Загрузка multipart, удаление, обновление списка после операций.

## Файлы

- `frontend/src/stores/admin.js` — Pinia store для документов
- `frontend/src/api/admin.js` — запросы к `/api/admin/documents*`

## Реализация

**State:** `documents` (array), `isUploading` (boolean).

**Actions:**

- `fetchDocuments()` — GET `/api/admin/documents`
- `uploadDocument(file, title, description)` — POST `/api/admin/documents` с `FormData`, выставить `isUploading`
- `deleteDocument(id)` — DELETE `/api/admin/documents/{id}`

Использовать общий HTTP-клиент. После успешной загрузки/удаления обновить `documents`.

## Критерии готовности

- Список документов загружается и отображается через store
- Загрузка и удаление работают с backend
- `isUploading` корректно отражает процесс загрузки
