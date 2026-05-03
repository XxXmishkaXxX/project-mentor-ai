# FE-106: ChatSidebar — боковая панель чатов

**Приоритет**: Must have
**Этап**: 1
**US**: US-01
**Зависимости**: FE-104, FE-113
**Статус**: не начата

> Референс: левая панель на всех скриншотах чата `20725313-3a41-4e4f-8344-c3863c5c6dd9.png`
> Подробное описание: `.cursor/docs/architecture/frontend_pages.md` → «3a: Sidebar»

## Описание

Боковая панель: кнопка нового чата, поиск, список чатов с группировкой по дате, профиль пользователя внизу. Полупрозрачный тёмный фон с backdrop-blur.

## Файлы

- `frontend/src/components/ChatSidebar.vue` — боковая панель чатов

## Визуальная спецификация

### Контейнер

- `width: 280px`, `height: 100vh`, `display: flex`, `flex-direction: column`
- `background: rgba(13, 16, 51, 0.9)`, `backdrop-filter: blur(20px)`
- `border-right: 1px solid var(--color-border)`
- `padding: 16px`

### Элементы (сверху вниз)

#### 1. Кнопка «+ Новый чат»

- `width: 100%`, `height: 42px`, `border-radius: var(--radius-md)`
- `background: var(--color-accent-gradient)` (фиолетовый градиент)
- `color: #fff`, `font-weight: 500`, `font-size: var(--font-size-base)`
- Иконка «+» слева от текста
- Hover: `box-shadow: var(--shadow-glow)`
- `margin-bottom: 12px`

#### 2. Поле поиска

- `<input type="text" placeholder="Поиск чатов...">`
- Иконка лупы слева внутри поля (через `padding-left: 36px` + абсолютная иконка)
- Стили: из дизайн-системы (input), `height: 38px`, `font-size: 13px`
- Фильтрует чаты на клиенте по `title` (case-insensitive `includes`)
- `margin-bottom: 16px`

#### 3. Список чатов (scrollable)

- `flex: 1`, `overflow-y: auto`
- **Группировка по дате**: сравнить `updated_at` с текущей датой
  - **Сегодня**: `updated_at` — сегодня
  - **Вчера**: `updated_at` — вчера
  - **Ранее**: всё остальное
- **Label группы**: `font-size: 11px`, `text-transform: uppercase`, `letter-spacing: 0.5px`, `color: var(--color-text-muted)`, `padding: 8px 8px 4px`, `margin-top: 8px`
- **Элемент чата**:
  - `padding: 10px 12px`, `border-radius: var(--radius-md)`, `cursor: pointer`
  - `display: flex`, `align-items: center`, `justify-content: space-between`
  - Текст: `title` обрезается с `text-overflow: ellipsis`, `white-space: nowrap`, `overflow: hidden`. `font-size: var(--font-size-base)`, `color: var(--color-text-primary)`
  - Если `title === null` → показать «Новый чат»
  - **Hover**: `background: var(--color-bg-surface-hover)`
  - **Активный** (`chatId === currentChatId`): `background: var(--color-bg-surface)`, `border-left: 3px solid var(--color-accent-primary)` (или `box-shadow: inset 3px 0 0 var(--color-accent-primary)`)
  - **Кнопка удаления**: иконка корзины, `opacity: 0` по умолчанию, `opacity: 1` при hover на элемент чата. `color: var(--color-text-muted)`, hover на иконке → `color: var(--color-accent-red)`. Клик → confirm-диалог «Удалить чат?» → `chatStore.deleteChat(id)`

#### 4. Профиль пользователя (прижат к низу)

- `margin-top: auto`, `padding-top: 16px`, `border-top: 1px solid var(--color-border)`
- `display: flex`, `align-items: center`, `gap: 12px`
- **Аватар**: круг `36px`, `background: var(--color-accent-primary)`, белая первая буква `username` по центру, `font-weight: 600`
- **Текст**: username (`font-size: 14px`, `font-weight: 500`), под ним role «Студент» (`font-size: 12px`, `color: var(--color-text-secondary)`)

## API

- `chatStore.fetchChats()` → `GET /api/chats/` → массив `ChatResponse[]`
- `chatStore.createChat()` → `POST /api/chats/` → `ChatResponse`
- `chatStore.deleteChat(id)` → `DELETE /api/chats/{chat_id}` → 204

## Поведение

- При нажатии «+ Новый чат»: `createChat()` → получить ответ с `id` → `router.push('/chat/' + id)`
- При клике на чат: `selectChat(id)` → `router.push('/chat/' + id)` → загрузка сообщений
- При удалении активного чата: удаление → `router.push('/chat')`
- При удалении неактивного чата: удаление, список обновляется, текущий чат не меняется
- Пустой список: показать текст «Начните первый диалог» по центру области списка

## Критерии готовности

- Кнопка «Новый чат» с фиолетовым градиентом
- Поиск фильтрует чаты на клиенте
- Чаты сгруппированы по датам (Сегодня/Вчера/Ранее)
- Активный чат визуально выделен
- Удаление с подтверждением
- Профиль пользователя внизу sidebar
