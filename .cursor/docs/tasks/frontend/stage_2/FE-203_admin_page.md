# FE-203: AdminPage — панель администратора

**Приоритет**: Should have
**Этап**: 2
**US**: US-12
**Зависимости**: FE-202, FE-113
**Статус**: не начата

> Референс: нижние правые блоки на `20725313-3a41-4e4f-8344-c3863c5c6dd9.png`
> Подробное описание: `.cursor/docs/architecture/frontend_pages.md` → «Страница 4: Админ-панель»

## Описание

Страница администратора для управления базой знаний. Собственный layout с боковой навигацией и областью контента. Доступна только пользователям с `role === 'admin'`.

## Файлы

- `frontend/src/pages/AdminPage.vue` — layout + координация компонентов

## Визуальная спецификация

### Layout

```
┌─────────────────┬──────────────────────────────────┐
│                 │  Content Header                   │
│   Admin         ├──────────────────────────────────┤
│   Sidebar       │                                  │
│   (250px)       │  Content Area                    │
│                 │  (DocumentUpload + DocumentList)  │
│                 │                                  │
└─────────────────┴──────────────────────────────────┘
```

- `display: flex`, `height: 100vh`, CosmicBackground на заднем плане

### Admin Sidebar

- `width: 250px`, `background: rgba(13, 16, 51, 0.9)`, `backdrop-filter: blur(20px)`, `border-right: 1px solid var(--color-border)`
- `display: flex`, `flex-direction: column`, `padding: 20px 0`

#### Логотип (вверху)

- `padding: 0 20px 24px`, `border-bottom: 1px solid var(--color-border)`, `margin-bottom: 16px`
- SVG-иконка щита + «Проектный Ассистент» — как на LoginPage, `font-size: 16px`

#### Навигация

- Вертикальный список пунктов меню, `padding: 0 12px`
- Каждый пункт: `display: flex`, `align-items: center`, `gap: 12px`, `padding: 10px 12px`, `border-radius: var(--radius-md)`, `cursor: pointer`, `font-size: var(--font-size-base)`, `color: var(--color-text-secondary)`
- Hover: `background: var(--color-bg-surface-hover)`, `color: var(--color-text-primary)`
- **Активный**: `background: var(--color-bg-surface)`, `color: var(--color-text-primary)`, `border-left: 3px solid var(--color-accent-primary)` (или на всю ширину с подсветкой)

**Пункты меню:**

| Иконка | Текст | Активный | Примечание |
|--------|-------|----------|------------|
| 📄 | Документы | да (по умолчанию) | Рабочий |
| 📊 | Статистика | нет | Заглушка (stage 3+) |
| 🔄 | Переиндексация | нет | Заглушка (stage 3) |
| 👥 | Пользователи | нет | Заглушка (future) |
| 🔗 | Обратная связь | нет | Заглушка (future) |
| ⚙️ | Настройки | нет | Заглушка (future) |

Неактивные пункты: визуально присутствуют, при клике — toast «Раздел в разработке»

#### Ссылка «Вернуться к чату»

- `margin-top: auto`, `padding: 16px 20px`, `border-top: 1px solid var(--color-border)`
- `<router-link to="/chat">← Вернуться к чату</router-link>`
- `color: var(--color-text-secondary)`, hover → `color: var(--color-text-primary)`

### Content Area

- `flex: 1`, `overflow-y: auto`, `padding: 32px`

#### Content Header

- `display: flex`, `align-items: center`, `justify-content: space-between`, `margin-bottom: 24px`
- **Слева**: «Документы» — `font-size: var(--font-size-xl)`, `font-weight: 600`
- **Справа**: кнопка «+ Загрузить документ»:
  - `background: var(--color-accent-green)`, `color: #fff`, `font-weight: 500`
  - `height: 40px`, `padding: 0 20px`, `border-radius: var(--radius-md)`
  - Иконка загрузки (↑) слева от текста
  - Hover: `filter: brightness(1.1)`
  - Клик → открытие `DocumentUpload` (модалка или inline-блок)

#### Табы фильтрации

- `display: flex`, `gap: 0`, `border-bottom: 1px solid var(--color-border)`, `margin-bottom: 24px`
- Каждый таб: `padding: 10px 20px`, `font-size: var(--font-size-base)`, `color: var(--color-text-secondary)`, `cursor: pointer`, `border-bottom: 2px solid transparent`
- Активный: `color: var(--color-text-primary)`, `border-bottom-color: var(--color-accent-primary)`
- Hover: `color: var(--color-text-primary)`

**Табы:**
- «Все документы (N)» — показывает все
- «Проиндексированные (N)» — фильтр `status === 'indexed'`
- «Ошибки (N)» — фильтр `status === 'error'`

Числа (N) — подсчёт из `adminStore.documents`

#### Содержимое

- Компонент `DocumentList` с отфильтрованными данными

## API при монтировании

- `adminStore.fetchDocuments()` → `GET /api/admin/documents`

## Поведение

- Guard: если `authStore.user.role !== 'admin'` → `router.push('/chat')`
- При монтировании: загрузить список документов
- Переключение табов: фильтрация на клиенте (без повторного запроса к API)
- Кнопка «Загрузить» → модалка/блок DocumentUpload

## Критерии готовности

- Layout с боковой навигацией и контентом
- Навигация: «Документы» активна, остальные — заглушки с toast
- Табы фильтрации с подсчётом
- Кнопка загрузки документа
- Ссылка возврата к чату
- Доступ только для admin
