# FE-108: MessageBubble — пузырь сообщения

**Приоритет**: Must have
**Этап**: 1
**US**: US-02
**Зависимости**: FE-113
**Статус**: не начата

> Референс: сообщения в чате на `20725313-3a41-4e4f-8344-c3863c5c6dd9.png`
> Подробное описание: `.cursor/docs/architecture/frontend_pages.md` → «Сообщение пользователя / ассистента»

## Описание

Компонент одного сообщения чата. Различает роли `user` и `assistant` по расположению, цвету и форме. Ответ ассистента поддерживает Markdown, блок источников и кнопки действий (копировать, отзыв).

## Файлы

- `frontend/src/components/MessageBubble.vue` — презентация одного сообщения

## Props

```typescript
interface Props {
  message: {
    id: string
    role: 'user' | 'assistant' | 'system'
    content: string
    sources?: Array<{
      document_title: string
      chunk_text: string
      score?: number
    }> | null
    created_at: string
  }
}
```

## Визуальная спецификация

### Сообщение пользователя (`role: 'user'`)

- **Расположение**: `align-self: flex-end` (справа), `max-width: 70%`
- **Пузырь**:
  - `background: var(--color-user-bubble)` — `linear-gradient(135deg, #6C5CE7, #8B5CF6)`
  - `color: #FFFFFF`
  - `border-radius: 16px 16px 4px 16px` (хвостик справа внизу)
  - `padding: 12px 18px`
  - `font-size: var(--font-size-base)`
  - `line-height: 1.5`
- **Время**: под пузырём справа, `font-size: var(--font-size-xs)` (11px), `color: var(--color-text-muted)`, `margin-top: 4px`
  - Формат: `HH:MM` (часы:минуты из `created_at`)
- **Анимация**: `fadeInUp` при появлении

### Сообщение ассистента (`role: 'assistant'`)

- **Расположение**: `align-self: flex-start` (слева), `max-width: 80%`
- **Аватар**: слева от пузыря, `width: 32px`, `height: 32px`, `border-radius: 50%`, `background: var(--color-bg-surface)`, иконка бота (SVG) по центру. `flex-shrink: 0`. `margin-right: 12px`
- **Пузырь**:
  - `background: var(--color-assistant-bubble)` — `#121438`
  - `border: 1px solid var(--color-border)`
  - `border-radius: 16px 16px 16px 4px` (хвостик слева внизу)
  - `padding: 16px 20px`
  - `color: var(--color-text-primary)`

#### Контент (Markdown)

- Рендерить HTML из Markdown с помощью `marked` (или `markdown-it`)
- Санитизация: `DOMPurify.sanitize(html)`
- Стили для рендеренного HTML:
  - Заголовки (`h1`–`h3`): `font-weight: 600`, `margin: 16px 0 8px`
  - Списки (`ol`, `ul`): `padding-left: 20px`, `margin: 8px 0`
  - `li`: `margin: 4px 0`
  - `code` (inline): `background: rgba(108, 92, 231, 0.15)`, `padding: 2px 6px`, `border-radius: 4px`, `font-family: 'JetBrains Mono', monospace`, `font-size: 13px`
  - `pre > code`: блок кода, `background: rgba(0, 0, 0, 0.3)`, `padding: 12px 16px`, `border-radius: 8px`, `overflow-x: auto`
  - `strong`: `font-weight: 600`
  - `em`: `font-style: italic`
  - `a`: `color: var(--color-accent-primary)`

#### Блок источников

- Появляется внутри пузыря ассистента, внизу после текста
- Только если `sources` массив непустой
- `background: rgba(108, 92, 231, 0.08)`, `border-radius: var(--radius-md)`, `padding: 12px`, `margin-top: 12px`
- Заголовок: «Источники» с иконкой книги, `font-size: 13px`, `font-weight: 600`, `color: var(--color-text-secondary)`, `margin-bottom: 8px`
- Нумерованный список источников:
  - `font-size: 13px`, `color: var(--color-accent-primary)`
  - Текст: `document_title` — кликабельный
  - Hover: `text-decoration: underline`
  - Клик → `$emit('open-source', { sources, index })`

#### Кнопки действий

- Ряд под пузырём, `display: flex`, `gap: 8px`, `margin-top: 8px`
- Иконочные кнопки (`24px`), `color: var(--color-text-muted)`, hover → `color: var(--color-text-secondary)`
- Кнопки:
  - 👍 Like → `$emit('feedback', { messageId, type: 'like' })`
  - 👎 Dislike → `$emit('feedback', { messageId, type: 'dislike' })`
  - 📋 Копировать → `navigator.clipboard.writeText(content)`, toast «Скопировано!»
  - 💬 Отзыв → `$emit('open-feedback', messageId)`

### Сообщение системы (`role: 'system'`)

- Не отображается (пропускать) или показать мелким текстом по центру

## Поведение

- Во время стриминга: `content` ответа ассистента обновляется реактивно по мере прихода токенов. Markdown рендерится на каждое обновление (с дебаунсом ~100ms для производительности если нужно)
- Пустой `content` при `isStreaming` → показать индикатор «думает» (обрабатывается в ChatWindow)

## Критерии готовности

- Сообщения user (справа, фиолетовый градиент) и assistant (слева, тёмный фон) визуально различимы
- Markdown рендерится корректно (заголовки, списки, код, жирный, курсив)
- Блок источников отображается только при наличии, кликабельный
- Кнопки действий видны у ответов ассистента
- Время сообщения отображается
- Анимация появления работает
