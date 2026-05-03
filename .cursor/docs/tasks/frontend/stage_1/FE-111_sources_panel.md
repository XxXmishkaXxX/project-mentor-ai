# FE-111: SourcesPanel / SourceModal — просмотр источников

**Приоритет**: Must have
**Этап**: 1
**US**: US-07
**Зависимости**: FE-108, FE-113
**Статус**: не начата

> Референс: правый верхний блок на `20725313-3a41-4e4f-8344-c3863c5c6dd9.png` (модалка «Источник 1 из 2»)
> Подробное описание: `.cursor/docs/architecture/frontend_pages.md` → «Модальное окно: Просмотр источника»

## Описание

Модальное окно для просмотра полного текста источника RAG. Открывается при клике на ссылку источника в ответе ассистента. Поддерживает навигацию между несколькими источниками одного сообщения.

## Файлы

- `frontend/src/components/SourceModal.vue` — модальное окно просмотра источника

## Props / Events

```typescript
interface Props {
  sources: Array<{
    document_title: string
    chunk_text: string
    score?: number
  }>
  initialIndex: number  // какой источник открыть первым (0-based)
  visible: boolean
}

// Events:
// @close — закрытие модалки
```

## Визуальная спецификация

### Overlay

- `position: fixed`, `inset: 0`, `z-index: 1000`
- `background: var(--color-overlay)` — `rgba(0, 0, 0, 0.6)`
- `display: flex`, `align-items: center`, `justify-content: center`
- Клик по overlay (вне модалки) → закрытие

### Модальное окно

- `width: 600px`, `max-width: 90vw`, `max-height: 80vh`
- `background: var(--color-bg-elevated)` (#1E2148)
- `border: 1px solid var(--color-border)`
- `border-radius: var(--radius-xl)` (16px)
- `box-shadow: var(--shadow-modal)`
- `display: flex`, `flex-direction: column`
- Анимация появления: `fadeIn` overlay (0.2s) + `slideUp` контент (`translateY(20px) → 0`, 0.3s)

### Header модалки

- `padding: 20px 24px 16px`, `display: flex`, `align-items: center`, `justify-content: space-between`
- `border-bottom: 1px solid var(--color-border)`
- **Слева**: «Источник {N} из {total}» — `font-size: var(--font-size-base)`, `font-weight: 600`
  - Кнопки навигации: `←` и `→`, иконочные кнопки (`28px`), `border-radius: 6px`, `background: var(--color-bg-surface)`, `border: 1px solid var(--color-border)`
  - `←` disabled если `index === 0`, `→` disabled если `index === total - 1`
  - Клик → переключение индекса
- **Справа**: кнопка ✕ (`24px`), `color: var(--color-text-secondary)`, hover → `color: var(--color-text-primary)`

### Тело модалки (scrollable)

- `padding: 24px`, `flex: 1`, `overflow-y: auto`

#### Название документа

- `font-size: var(--font-size-lg)` (20px), `font-weight: 600`, `color: var(--color-text-primary)`
- `margin-bottom: 16px`
- Текст: `sources[currentIndex].document_title`

#### Текст фрагмента

- `font-size: var(--font-size-base)`, `line-height: 1.7`, `color: var(--color-text-secondary)`
- Текст: `sources[currentIndex].chunk_text`
- Может быть длинным — поэтому `overflow-y: auto` на теле

#### Метаданные (footer внутри тела)

- `margin-top: 20px`, `padding-top: 16px`, `border-top: 1px solid var(--color-border)`
- Если `score` есть: «Релевантность: 92%» — `font-size: 13px`, `color: var(--color-text-muted)`
- Формат score: `Math.round(score * 100) + '%'`

## Поведение

- **Открытие**: MessageBubble → `$emit('open-source', { sources, index })` → ChatPage устанавливает `sourceModalVisible = true` и передаёт props
- **Закрытие**: кнопка ✕, клик по overlay, или `Escape`
- **Навигация**: стрелки ←/→ в header, также клавиши `ArrowLeft` / `ArrowRight`
- **Переходы**: при смене индекса — лёгкий `fade` переход контента (0.2s)
- **Body scroll lock**: при открытии модалки — `document.body.style.overflow = 'hidden'`, при закрытии — восстановить

## Edge cases

- Если `sources` пустой массив или undefined → не открывать модалку
- Если `document_title` не задан → показать «Без названия»
- Если `chunk_text` очень длинный → `overflow-y: auto` в теле, полная прокрутка

## Критерии готовности

- Модалка открывается при клике на источник в ответе ассистента
- Навигация «Источник 1 из N» переключает между источниками
- Отображается название документа и полный текст фрагмента
- Закрытие: ✕, overlay, Escape
- Анимация появления/исчезновения
- Score отображается как процент если доступен
