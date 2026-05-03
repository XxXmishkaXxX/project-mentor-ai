# FE-109: ChatInput — поле ввода сообщения

**Приоритет**: Must have
**Этап**: 1
**US**: US-02
**Зависимости**: FE-104, FE-113
**Статус**: не начата

> Референс: нижняя часть чата на `20725313-3a41-4e4f-8344-c3863c5c6dd9.png`
> Подробное описание: `.cursor/docs/architecture/frontend_pages.md` → «3d: Поле ввода»

## Описание

Многострочное поле ввода с автоувеличением высоты, круглой кнопкой отправки, блокировкой во время стриминга. Отправка по Enter, новая строка по Shift+Enter.

## Файлы

- `frontend/src/components/ChatInput.vue` — textarea + кнопка отправки

## Визуальная спецификация

### Контейнер

- `padding: 16px 24px`, `background: rgba(13, 16, 51, 0.7)`, `backdrop-filter: blur(10px)`
- `border-top: 1px solid var(--color-border)`
- `position: relative`

### Textarea

- `width: 100%`, `min-height: 44px`, `max-height: 200px`
- `background: var(--color-bg-surface)` (#121438)
- `border: 1px solid var(--color-border)`, focus → `border-color: var(--color-border-focus)`
- `border-radius: 12px`
- `padding: 12px 56px 12px 16px` (правый padding для кнопки)
- `color: var(--color-text-primary)`, `font-size: var(--font-size-base)`, `font-family: inherit`
- `resize: none`, `outline: none`
- Placeholder: «Задайте вопрос...», `color: var(--color-text-muted)`
- **Авторазмер**: высота автоматически растёт с контентом, через `scrollHeight`. При `max-height` → внутренний `overflow-y: auto`
- Disabled при `chatStore.isStreaming`: `opacity: 0.5`, `cursor: not-allowed`

### Кнопка отправки

- `position: absolute`, `right: 32px`, `bottom: 24px` (внутри контейнера, справа от textarea)
- Круг: `width: 40px`, `height: 40px`, `border-radius: 50%`
- `background: var(--color-accent-gradient)` (фиолетовый градиент)
- Иконка стрелки вверх (↑) по центру, `color: #fff`
- **Enabled** (текст не пустой и не стриминг): `opacity: 1`, `cursor: pointer`, hover → `box-shadow: var(--shadow-glow)`
- **Disabled** (текст пустой или стриминг): `opacity: 0.4`, `cursor: not-allowed`
- Клик → `$emit('send', content)` (или прямой вызов `chatStore.sendMessage`)

### Подсказка

- Под textarea, `font-size: var(--font-size-xs)`, `color: var(--color-text-muted)`
- Текст: «Shift + Enter для новой строки»

## Поведение

### Клавиатура

- `Enter` (без Shift) → отправка сообщения (если текст не пустой и не стриминг)
- `Shift + Enter` → перенос строки (стандартное поведение textarea)
- `Ctrl + Enter` / `Cmd + Enter` → тоже отправка (опционально)

### Отправка

1. Проверить: `content.trim().length > 0` и `!chatStore.isStreaming`
2. Сохранить текст, очистить textarea, сбросить высоту к `min-height`
3. Если нет `currentChatId` → `chatStore.createChat()` сначала, получить `chatId`
4. `chatStore.sendMessage(chatId, content)` → начинается SSE-стриминг
5. Textarea и кнопка блокируются до завершения стриминга

### Фокус

- При монтировании компонента → `textarea.focus()`
- После завершения стриминга → `textarea.focus()` для следующего вопроса

## Критерии готовности

- Textarea авторастёт по содержимому до max-height
- Кнопка отправки — круглая с градиентом, disabled когда пусто или стриминг
- Enter отправляет, Shift+Enter — новая строка
- Пустые/пробельные сообщения не отправляются
- Поле очищается после отправки
- Подсказка «Shift + Enter для новой строки» видна
