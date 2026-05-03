# FE-113: Дизайн-система и глобальные стили

**Приоритет**: Блокирующий (все компоненты зависят от стилей)
**Этап**: 1
**US**: US-01
**Зависимости**: FE-001
**Статус**: не начата

> Референс дизайна: `20725313-3a41-4e4f-8344-c3863c5c6dd9.png`
> Подробное описание: `.cursor/docs/architecture/frontend_pages.md`

## Описание

Единая дизайн-система тёмной «космической» темы: CSS-переменные всех цветов, типографика, глобальные стили, reset/normalize, утилитарные классы. Анимированный фон с частицами и линиями (космос/констелляция), отображающийся на всех страницах.

## Файлы

- `frontend/src/assets/styles/variables.css` — все CSS custom properties
- `frontend/src/assets/styles/reset.css` — reset/normalize
- `frontend/src/assets/styles/base.css` — стили body, типографика, input, button, textarea, links
- `frontend/src/assets/styles/animations.css` — keyframes для fadeInUp, pulse, skeleton и др.
- `frontend/src/assets/styles/utilities.css` — утилитарные классы (truncate, sr-only и т.д.)
- `frontend/src/assets/styles/main.css` — единый импорт всех файлов стилей
- `frontend/src/components/CosmicBackground.vue` — компонент анимированного фона
- `frontend/src/main.js` — импорт `main.css` + подключение шрифта Inter

## Реализация

### CSS-переменные (`variables.css`)

```css
:root {
  /* Backgrounds */
  --color-bg-primary: #070B1A;
  --color-bg-secondary: #0D1033;
  --color-bg-surface: #121438;
  --color-bg-surface-hover: #1A1D4E;
  --color-bg-elevated: #1E2148;

  /* Accents */
  --color-accent-primary: #6C5CE7;
  --color-accent-gradient: linear-gradient(135deg, #6C5CE7, #A855F7);
  --color-accent-green: #00D68F;
  --color-accent-red: #FF4757;
  --color-accent-yellow: #FFA502;

  /* Text */
  --color-text-primary: #FFFFFF;
  --color-text-secondary: #8B8BA7;
  --color-text-muted: #5B5B7B;

  /* Borders */
  --color-border: rgba(255, 255, 255, 0.08);
  --color-border-focus: rgba(108, 92, 231, 0.5);

  /* Chat bubbles */
  --color-user-bubble: linear-gradient(135deg, #6C5CE7, #8B5CF6);
  --color-assistant-bubble: #121438;

  /* Overlay */
  --color-overlay: rgba(0, 0, 0, 0.6);

  /* Shadows */
  --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.3);
  --shadow-modal: 0 8px 32px rgba(0, 0, 0, 0.5);
  --shadow-glow: 0 0 20px rgba(108, 92, 231, 0.3);

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 50%;

  /* Typography */
  --font-family: 'Inter', system-ui, -apple-system, sans-serif;
  --font-size-xs: 11px;
  --font-size-sm: 12px;
  --font-size-base: 14px;
  --font-size-md: 16px;
  --font-size-lg: 20px;
  --font-size-xl: 24px;

  /* Transitions */
  --transition-fast: 0.15s ease;
  --transition-base: 0.2s ease;
  --transition-slow: 0.3s ease;
}
```

### Подключение шрифта

В `index.html` подключить Google Fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Базовые стили (`base.css`)

- `body`: `margin: 0`, `font-family: var(--font-family)`, `font-size: var(--font-size-base)`, `color: var(--color-text-primary)`, `background: var(--color-bg-primary)`, `line-height: 1.5`, `-webkit-font-smoothing: antialiased`
- `input, textarea`: `background: rgba(18, 20, 56, 0.6)`, `border: 1px solid var(--color-border)`, `border-radius: var(--radius-md)`, `color: #fff`, `padding: 0 16px`, `height: 44px`, `font-family: inherit`, `font-size: var(--font-size-base)`, `outline: none`, `transition: border-color var(--transition-base)`. Focus → `border-color: var(--color-border-focus)`
- `button`: `cursor: pointer`, `font-family: inherit`, `border: none`, `transition: all var(--transition-base)`
- `a`: `color: var(--color-accent-primary)`, `text-decoration: none`. Hover → `text-decoration: underline`
- `*`: `box-sizing: border-box`, `margin: 0`, `padding: 0`
- Scrollbar (webkit): тонкий стиль, `track: transparent`, `thumb: var(--color-bg-surface-hover)`, `width: 6px`

### Анимации (`animations.css`)

```css
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

@keyframes skeleton {
  0% { background-position: -200px 0; }
  100% { background-position: calc(200px + 100%) 0; }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### Компонент CosmicBackground.vue

Полноэкранный Canvas-элемент (`position: fixed`, `inset: 0`, `z-index: 0`, `pointer-events: none`).

- **Фоновый градиент**: радиальный от `#0D1033` в центре к `#070B1A` по краям
- **Частицы**: 60–100 точек, случайные позиции, размер 1–3px, цвет `rgba(108, 92, 231, alpha)` и `rgba(255, 255, 255, alpha)` где alpha 0.3–0.8
- **Движение**: каждая частица имеет `vx`, `vy` (скорость ±0.3–0.8 px/frame); при выходе за границы — перенос на противоположную сторону
- **Линии**: между частицами ближе ~150px рисовать линию с `strokeStyle: rgba(108, 92, 231, opacity)` где opacity = 1 - (distance / 150)
- **Рендер**: `requestAnimationFrame`, очистка → рисование линий → рисование точек
- **Подключение**: в `App.vue` как первый дочерний элемент (или в `<template>` каждой страницы через layout)

Весь UI-контент располагается поверх фона с `position: relative; z-index: 1`.

## Критерии готовности

- Все CSS-переменные определены и доступны во всех компонентах
- Шрифт Inter загружается, fallback работает
- Body и базовые элементы стилизованы в тёмной теме
- Анимированный космический фон виден на всех страницах
- Фон не влияет на производительность (60 fps)
- Скроллбар стилизован
- Все последующие компоненты могут использовать переменные через `var(--...)`
