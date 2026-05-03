# FE-105: ChatPage — основной layout чата

**Приоритет**: Must have
**Этап**: 1
**US**: US-01, US-02
**Зависимости**: FE-104, FE-113
**Статус**: не начата

> Референс: центральный и нижний ряд на `20725313-3a41-4e4f-8344-c3863c5c6dd9.png`
> Подробное описание: `.cursor/docs/architecture/frontend_pages.md` → «Страница 3: Чат»

## Описание

Главная страница приложения после входа. Трёхзонный layout: боковая панель с чатами (слева), область сообщений (центр), поле ввода (прижато к низу). Анимированный фон виден через полупрозрачные элементы.

## Файлы

- `frontend/src/pages/ChatPage.vue` — layout и координация дочерних компонентов

## Визуальная спецификация

### Layout

```
┌─────────────────┬──────────────────────────────────┐
│                 │  ChatHeader (60px)                │
│   ChatSidebar   ├──────────────────────────────────┤
│   (280px)       │                                  │
│                 │  ChatWindow / ExampleQuestions     │
│   fixed height  │  (flex: 1, overflow-y: auto)      │
│                 │                                  │
│                 ├──────────────────────────────────┤
│                 │  ChatInput (~80px)                │
└─────────────────┴──────────────────────────────────┘
```

- Контейнер: `display: flex`, `height: 100vh`, `position: relative`, `z-index: 1`
- Анимированный фон (CosmicBackground) за layout'ом
- Sidebar: фиксированная ширина `280px`
- Правая часть: `display: flex`, `flex-direction: column`, `flex: 1`, `min-width: 0`
  - ChatHeader: `flex-shrink: 0`
  - ChatWindow или ExampleQuestions: `flex: 1`, `overflow-y: auto`
  - ChatInput: `flex-shrink: 0`

### ChatHeader

- `height: 60px`, `padding: 0 24px`, `display: flex`, `align-items: center`, `justify-content: space-between`
- `background: rgba(13, 16, 51, 0.5)`, `backdrop-filter: blur(10px)`, `border-bottom: 1px solid var(--color-border)`
- **Слева**: title чата — `font-size: var(--font-size-lg)`, `font-weight: 600`. Если `title === null` → «Новый чат»
- **Справа**: кнопка «Поделиться» (иконка, ghost-стиль) + кнопка «⋯» (3 точки, dropdown-меню: «Переименовать», «Удалить»)

### Логика переключения контента

- Если `chatStore.messages.length === 0` для текущего чата → показать `ExampleQuestions`
- Если есть сообщения → показать `ChatWindow`
- Между ними — `ChatInput` всегда виден

### Маршрутизация

- `/chat` → новый чат (`currentChatId = null`), показать ExampleQuestions
- `/chat/:id` → `chatStore.selectChat(id)` при монтировании и при смене `route.params.id` (через `watch`)
  - Если чат не найден (404) → показать toast «Чат не найден» + редирект на `/chat`

## API при монтировании

1. `chatStore.fetchChats()` — загрузить список чатов для sidebar
2. Если `route.params.id` → `chatStore.selectChat(id)` → `chatStore.fetchMessages(id)`

## Поведение

- При создании нового чата: `createChat()` → получить `chatId` → `router.push('/chat/' + chatId)`
- При удалении текущего чата: `deleteChat(id)` → `router.push('/chat')`
- При `authStore.logout()` → `router.push('/login')`

## Критерии готовности

- Layout стабилен на desktop (sidebar + контент)
- Анимированный фон виден за полупрозрачными элементами
- Пустой чат показывает ExampleQuestions, заполненный — ChatWindow
- Переключение чатов через sidebar и URL корректно
- Header показывает название чата
