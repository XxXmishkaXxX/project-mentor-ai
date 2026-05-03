# FE-110: ExampleQuestions — приветственный экран

**Приоритет**: Must have
**Этап**: 1
**US**: US-01
**Зависимости**: FE-104, FE-113
**Статус**: не начата

> Референс: нижний левый блок чата (с роботом) на `20725313-3a41-4e4f-8344-c3863c5c6dd9.png`
> Подробное описание: `.cursor/docs/architecture/frontend_pages.md` → «3c: Область сообщений — пустой чат»

## Описание

Приветственный экран, отображаемый в пустом чате (нет сообщений). Иконка ассистента, приветственный текст, сетка карточек с примерами вопросов. Клик по карточке создаёт чат и отправляет вопрос.

## Файлы

- `frontend/src/components/ExampleQuestions.vue` — приветственный экран с карточками

## Визуальная спецификация

### Контейнер

- `display: flex`, `flex-direction: column`, `align-items: center`, `justify-content: center`
- `flex: 1` (занимает всё доступное пространство ChatWindow)
- `padding: 40px 24px`
- Фон: прозрачный (космический фон виден)

### Элементы (сверху вниз)

#### 1. Иконка ассистента

- `width: 80px`, `height: 80px`, `margin-bottom: 24px`
- Стилизованная иконка: аватар бота / три точки чата в круге
- `background: rgba(108, 92, 231, 0.15)`, `border-radius: 50%`
- Иконка внутри `color: var(--color-accent-primary)`, `font-size: 36px`
- Лёгкий glow: `box-shadow: 0 0 40px rgba(108, 92, 231, 0.2)`

#### 2. Заголовок

- «Привет! Я ваш проектный ассистент»
- `font-size: var(--font-size-xl)` (24px), `font-weight: 600`, `color: var(--color-text-primary)`
- `text-align: center`, `margin-bottom: 12px`

#### 3. Подзаголовок

- «Задавайте вопросы по управлению проектами, Agile, Scrum, DevOps и другим практикам.»
- `font-size: var(--font-size-base)` (14px), `color: var(--color-text-secondary)`
- `text-align: center`, `max-width: 500px`, `margin-bottom: 32px`

#### 4. Метка

- «Примеры вопросов:»
- `font-size: 13px`, `color: var(--color-text-secondary)`, `margin-bottom: 16px`
- `align-self: flex-start` (или по центру)

#### 5. Сетка карточек

- `display: grid`, `grid-template-columns: 1fr 1fr`, `gap: 12px`, `max-width: 600px`, `width: 100%`

**Каждая карточка:**
- `background: rgba(18, 20, 56, 0.6)`
- `border: 1px solid var(--color-border)`
- `border-radius: var(--radius-lg)` (12px)
- `padding: 14px 18px`
- `cursor: pointer`
- `display: flex`, `align-items: center`, `justify-content: space-between`
- Текст: `font-size: var(--font-size-base)`, `color: var(--color-text-primary)`
- Справа: иконка стрелки «→», `color: var(--color-accent-primary)`, `font-size: 16px`
- **Hover**: `border-color: var(--color-accent-primary)`, `background: rgba(108, 92, 231, 0.1)`, `transition: all var(--transition-base)`

**Тексты карточек (захардкожены):**

| # | Текст |
|---|-------|
| 1 | Как правильно составить ТЗ? |
| 2 | Какие этапы у Scrum? |
| 3 | Как распределить роли в команде? |
| 4 | Что такое Kanban? |

## Поведение при клике

1. Пользователь кликает на карточку
2. Если `chatStore.currentChatId === null`:
   - `await chatStore.createChat()` → получить `chatId`
   - `router.push('/chat/' + chatId)`
3. `await chatStore.sendMessage(chatId, questionText)` — отправить текст карточки как сообщение
4. Компонент ExampleQuestions скрывается (т.к. теперь есть сообщения)

## Скрытие

- Компонент показывается только когда `chatStore.messages.length === 0` для текущего чата
- Как только отправлено первое сообщение → ExampleQuestions скрывается, ChatWindow с сообщениями появляется

## Критерии готовности

- Иконка бота с glow-эффектом по центру
- Приветственный текст и подзаголовок
- Сетка 2x2 с карточками-вопросами
- Hover-эффект на карточках (подсветка фиолетовым)
- Клик создаёт чат и отправляет вопрос
- При появлении сообщений экран скрывается
