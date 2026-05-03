# US-12: Загрузка документов в базу знаний

**Приоритет**: Should have
**Итерация**: 2
**Модуль**: admin
**Backend**: `backend/src/app/admin/controller.py`, `admin/service.py`
**Frontend**: `AdminPage.vue`, `DocumentUpload.vue`, `DocumentList.vue`

## Формулировка

Как администратор базы знаний, я хочу загрузить новый документ через интерфейс или служебный механизм, чтобы обновлять знания ассистента без изменения основной логики сайта.

## Критерии приёмки

- администратор может добавить документ в базу знаний
- система обрабатывает документ и разбивает его на фрагменты
- фрагменты сохраняются в векторной базе данных
- новый документ используется при последующих запросах
- при ошибке загрузки система сообщает причину

## Технические детали

POST `/api/admin/documents` (multipart). Backend: save file → create document record (`status=processing`) → chunking → embedding → upsert Qdrant → update `status=indexed`.
