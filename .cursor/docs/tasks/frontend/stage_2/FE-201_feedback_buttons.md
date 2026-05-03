# FE-201: FeedbackButtons + FeedbackModal — отзыв на ответ

**Приоритет**: Should have
**Этап**: 2
**US**: US-10
**Зависимости**: BE-202, FE-108, FE-113
**Статус**: не начата

> Референс: правый блок с emoji на `20725313-3a41-4e4f-8344-c3863c5c6dd9.png`
> Подробное описание: `.cursor/docs/architecture/frontend_pages.md` → «Модальное окно: Отзыв»

## Описание

Кнопки like/dislike и «Оставить отзыв» под ответами ассистента, плюс модальное окно с 5-балльной emoji-оценкой и необязательным комментарием. Обратная связь отправляется на backend API.

## Файлы

- `frontend/src/components/FeedbackButtons.vue` — ряд кнопок под ответом
- `frontend/src/components/FeedbackModal.vue` — модальное окно с формой отзыва

## FeedbackButtons

### Props

```typescript
interface Props {
  messageId: string
  currentFeedback?: 'like' | 'dislike' | null
}
```

### Визуал

- `display: flex`, `gap: 8px`, `margin-top: 8px`
- Иконочные кнопки: `width: 28px`, `height: 28px`, `border-radius: 6px`, `background: transparent`, `border: none`
- `color: var(--color-text-muted)`, `font-size: 14px`
- Hover: `color: var(--color-text-secondary)`, `background: var(--color-bg-surface-hover)`
- **Активная** (выбранная): `color: var(--color-accent-primary)`, `background: rgba(108, 92, 231, 0.15)`
- Кнопки: 👍, 👎, 📋 (копировать), 💬 (открыть FeedbackModal)

### Поведение

- 👍 клик → отправить feedback `type: 'like'`, подсветить кнопку. Повторный клик → отменить
- 👎 клик → отправить feedback `type: 'dislike'`, подсветить. Клик на 👍 после 👎 → заменить
- 📋 → `navigator.clipboard.writeText(content)` → toast «Скопировано!»
- 💬 → `$emit('open-feedback', messageId)` → открывает FeedbackModal

## FeedbackModal

### Визуал

- **Overlay**: `var(--color-overlay)`, клик → закрытие
- **Модалка**: `width: 480px`, `max-width: 90vw`, `background: var(--color-bg-elevated)`, `border-radius: var(--radius-xl)`, `padding: 32px`, `box-shadow: var(--shadow-modal)`

### Содержимое

1. **Header**: «Ваш отзыв помогает нам стать лучше» (`font-size: var(--font-size-lg)`, `font-weight: 600`), кнопка ✕ справа

2. **Вопрос**: «Был ли ответ полезен?» — `font-size: var(--font-size-base)`, `color: var(--color-text-secondary)`, `margin: 16px 0`

3. **5 emoji-кнопок** в ряд (`display: flex`, `gap: 12px`, `justify-content: center`, `margin-bottom: 24px`):

   | Emoji | Значение | Rating |
   |-------|----------|--------|
   | 😡 | Ужасно | 1 |
   | 😕 | Плохо | 2 |
   | 😐 | Нормально | 3 |
   | 🙂 | Хорошо | 4 |
   | 😍 | Отлично | 5 |

   Каждая кнопка:
   - `width: 56px`, `height: 56px`, `border-radius: var(--radius-lg)` (12px)
   - `background: var(--color-bg-surface)`, `border: 1px solid var(--color-border)`
   - `font-size: 24px`, `cursor: pointer`
   - Hover: `border-color: var(--color-accent-primary)`, `transform: scale(1.1)`, `transition: all var(--transition-fast)`
   - Выбранная: `border-color: var(--color-accent-primary)`, `background: rgba(108, 92, 231, 0.15)`, `box-shadow: 0 0 12px rgba(108, 92, 231, 0.3)`

4. **Textarea «Комментарий (необязательно)»**:
   - `width: 100%`, `height: 100px`, `resize: vertical`
   - Placeholder: «Что можно улучшить?»
   - Стили из дизайн-системы (тёмный input)
   - `margin-bottom: 20px`

5. **Кнопка «Отправить»**:
   - `width: 100%`, `height: 44px`, `border-radius: var(--radius-md)`
   - `background: var(--color-accent-gradient)` (фиолетовый градиент)
   - `color: #fff`, `font-weight: 600`
   - Disabled пока emoji не выбрано: `opacity: 0.5`
   - Loading: спиннер при отправке

### API

```
POST /api/messages/{messageId}/feedback
Content-Type: application/json
Body: { "rating": 1-5, "comment": "string | null" }
```

- Успех → закрыть модалку, toast «Спасибо за отзыв!» (зелёный)
- Ошибка → toast «Не удалось отправить отзыв» (красный)

> Примечание: если endpoint feedback ещё не реализован на бэке, показывать toast «Спасибо за отзыв!» (mock, сохраняя UX) и логировать в console.

### Поведение

- Закрытие: ✕, overlay, Escape
- При повторном открытии: сброс состояния (выбранный emoji, комментарий)
- Body scroll lock при открытии

## Критерии готовности

- Кнопки 👍/👎/📋/💬 видны под ответами ассистента
- Like/dislike визуально подсвечиваются при выборе
- Копирование работает + toast
- FeedbackModal открывается с 5 emoji и textarea
- Кнопка «Отправить» disabled без выбора emoji
- Отправка на API (или mock) с feedback
