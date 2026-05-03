# FE-102: LoginPage — страница входа

**Приоритет**: Must have
**Этап**: 1
**US**: US-01
**Зависимости**: FE-101, FE-113
**Статус**: не начата

> Референс: левый верхний блок на `20725313-3a41-4e4f-8344-c3863c5c6dd9.png`
> Подробное описание: `.cursor/docs/architecture/frontend_pages.md` → «Страница 1: Вход»

## Описание

Страница входа с формой по центру экрана поверх анимированного космического фона. Тёмная полупрозрачная карточка с backdrop-blur, логотип приложения, поля email/пароль, кнопка входа и ссылка на регистрацию.

## Файлы

- `frontend/src/pages/LoginPage.vue` — страница входа

## Визуальная спецификация

### Layout

- Анимированный фон (CosmicBackground) на весь экран
- Карточка формы: по центру экрана (`display: flex; align-items: center; justify-content: center; min-height: 100vh`)

### Карточка формы

- `width: 420px`, `max-width: 90vw` (для мобильных)
- `background: rgba(13, 16, 51, 0.85)`
- `backdrop-filter: blur(20px)`
- `border: 1px solid var(--color-border)`
- `border-radius: var(--radius-xl)` (16px)
- `padding: 40px`
- `box-shadow: var(--shadow-card)`

### Элементы карточки (сверху вниз)

1. **Логотип**: SVG-иконка щита (~40px) + текст «Проектный Ассистент» (`font-size: 18px`, `font-weight: 700`, `color: var(--color-text-primary)`). Под ним: «Ваш ИИ-ментор в проектной деятельности» (`font-size: 13px`, `color: var(--color-text-secondary)`). `margin-bottom: 32px`, `text-align: center`

2. **Заголовок**: «Вход в систему» — `font-size: var(--font-size-lg)` (20px), `font-weight: 600`. Подзаголовок: «Добро пожаловать! Войдите в свой аккаунт» — `font-size: var(--font-size-base)`, `color: var(--color-text-secondary)`. `margin-bottom: 24px`

3. **Поле Email**: `<label>Email</label>` + `<input type="email" placeholder="you@example.com">`. Стили ввода из дизайн-системы (FE-113). `margin-bottom: 16px`

4. **Поле Пароль**: `<label>Пароль</label>` + `<input type="password">`. Справа внутри поля — иконка 👁 для toggle показа пароля. `margin-bottom: 16px`

5. **Ряд**: слева `<label><input type="checkbox"> Запомнить меня</label>` (`font-size: 13px`, `color: var(--color-text-secondary)`), справа «Забыли пароль?» (`color: var(--color-text-secondary)`, `cursor: default` — неактивная на stage 1). `margin-bottom: 24px`

6. **Кнопка «Войти»**: `width: 100%`, `height: 48px`, `background: var(--color-accent-green)` (#00D68F), `color: #fff`, `font-weight: 600`, `font-size: var(--font-size-base)`, `border-radius: var(--radius-md)`. Hover: `filter: brightness(1.1)`. Disabled: `opacity: 0.6`, `cursor: not-allowed`. Loading: текст заменяется на спиннер (CSS spin). `margin-bottom: 24px`

7. **Ссылка**: «Нет аккаунта?» + `<router-link to="/register">Зарегистрироваться</router-link>` — `text-align: center`, `font-size: var(--font-size-base)`, ссылка `color: var(--color-accent-primary)`

### Сообщение об ошибке

- При ошибке API: красный текст (`color: var(--color-accent-red)`, `font-size: 13px`) появляется между паролем и чекбоксом (или под кнопкой)
- Анимация появления: `fadeInUp`

## API-интеграция

### Отправка формы

```
POST /api/auth/login
Content-Type: application/json
Body: { "email": "...", "password": "..." }
```

### Обработка ответов

| Код | Действие |
|-----|----------|
| 200 | Сервер ставит cookie `session_id`. Ответ: `UserResponse { id, username, email, role }`. Сохранить в `authStore.user`. Выполнить `router.push('/chat')` |
| 401 | Показать «Неверный email или пароль» — текст из `response.detail` |
| 422 | Показать ошибки валидации из `response.extra[]` под соответствующими полями |
| Network error | Показать «Ошибка сети. Проверьте подключение» |

## Клиентская валидация

- Email: обязательно, проверка regex `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`
- Пароль: обязательно, минимум 1 символ
- Кнопка «Войти» disabled пока оба поля не заполнены
- Ошибки валидации: красный текст под полем, `border-color: var(--color-accent-red)`

## Поведение

- При монтировании: если `authStore.isAuthenticated` → `router.push('/chat')`
- Фокус на поле Email при загрузке страницы
- Enter на любом поле → submit формы

## Критерии готовности

- Карточка центрирована поверх анимированного фона
- Форма стилизована в тёмной теме с полупрозрачной карточкой
- Валидация полей с визуальной обратной связью
- При успешном входе — переход на `/chat`
- При ошибке — понятное сообщение пользователю
- Кнопка показывает загрузку во время запроса
- Toggle видимости пароля работает
