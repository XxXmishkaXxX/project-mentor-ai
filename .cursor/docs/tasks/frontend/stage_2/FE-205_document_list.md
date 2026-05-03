# FE-205: DocumentList — таблица документов

**Приоритет**: Should have
**Этап**: 2
**US**: US-12
**Зависимости**: FE-202, FE-113
**Статус**: не начата

> Референс: правый нижний блок (таблица) на `20725313-3a41-4e4f-8344-c3863c5c6dd9.png`
> Подробное описание: `.cursor/docs/architecture/frontend_pages.md` → «Content: Документы — Таблица»

## Описание

Таблица документов базы знаний: название, тип файла, размер, статус с цветовыми бейджами, дата добавления, кнопки действий. Пагинация с нумерацией страниц.

## Файлы

- `frontend/src/components/DocumentList.vue` — таблица + пагинация

## Props

```typescript
interface Props {
  documents: Array<{
    id: string
    title: string
    filename: string
    file_type: string    // 'PDF', 'DOCX', 'MD'
    file_size: number    // в байтах
    status: 'indexed' | 'processing' | 'error' | 'pending'
    chunks_count?: number
    created_at: string
  }>
}
```

## Визуальная спецификация

### Контейнер таблицы

- `background: rgba(13, 16, 51, 0.5)`, `border: 1px solid var(--color-border)`, `border-radius: var(--radius-lg)`, `overflow: hidden`

### Header таблицы

- `background: rgba(18, 20, 56, 0.8)`
- Ячейки: `padding: 12px 16px`, `font-size: 13px`, `font-weight: 600`, `color: var(--color-text-secondary)`, `text-transform: uppercase`, `letter-spacing: 0.5px`

### Колонки

| Колонка | Ширина | Содержимое |
|---------|--------|------------|
| Название | flex: 2 | `title` — `font-weight: 500`, `color: var(--color-text-primary)` |
| Тип | 80px | `file_type` — бейдж `PDF` / `DOCX` / `MD` |
| Размер | 100px | `formatFileSize(file_size)` — «1.2 МБ», «892 КБ» |
| Статус | 160px | Цветной бейдж (см. ниже) |
| Дата добавления | 140px | `formatDate(created_at)` — «12.05.2024» |
| Действия | 80px | Иконки (редактировать, удалить) |

### Строки таблицы

- `padding: 14px 16px`, `border-bottom: 1px solid var(--color-border)`
- Hover: `background: var(--color-bg-surface-hover)`
- `transition: background var(--transition-fast)`

### Статус-бейджи

| Статус | Текст | Background | Color |
|--------|-------|------------|-------|
| `indexed` | Проиндексирован | `rgba(0, 214, 143, 0.15)` | `#00D68F` |
| `processing` | В обработке | `rgba(255, 165, 2, 0.15)` | `#FFA502` |
| `error` | Ошибка индексации | `rgba(255, 71, 87, 0.15)` | `#FF4757` |
| `pending` | Ожидание | `rgba(91, 91, 123, 0.15)` | `#8B8BA7` |

Стили бейджа: `display: inline-flex`, `padding: 4px 10px`, `border-radius: var(--radius-sm)`, `font-size: 12px`, `font-weight: 500`

### Кнопки действий

- Иконки в ряд: `display: flex`, `gap: 8px`
- Каждая: `width: 28px`, `height: 28px`, `border-radius: 6px`, `background: transparent`, `border: none`
- `color: var(--color-text-muted)`, hover → `color: var(--color-text-secondary)`, `background: var(--color-bg-surface-hover)`
- Удаление hover: `color: var(--color-accent-red)`
- Удаление клик → confirm-диалог «Удалить документ "{title}"?» → `adminStore.deleteDocument(id)`

### Пагинация

- `display: flex`, `align-items: center`, `justify-content: center`, `gap: 4px`
- `padding: 16px`, `border-top: 1px solid var(--color-border)`
- Кнопки страниц: `width: 32px`, `height: 32px`, `border-radius: 6px`
  - Default: `background: transparent`, `color: var(--color-text-secondary)`, `border: 1px solid var(--color-border)`
  - Hover: `background: var(--color-bg-surface-hover)`
  - Активная: `background: var(--color-accent-primary)`, `color: #fff`
- Стрелки ← →: аналогичные кнопки. Disabled на первой/последней странице: `opacity: 0.3`
- Многоточие «...» между далёкими номерами

**Логика пагинации:**
- `itemsPerPage = 10` (или из store)
- Показывать: первая, последняя, текущая ±2, и `...` если есть промежутки
- Пример: `← 1 2 3 ... 16 →`
- При смене страницы: `adminStore.fetchDocuments({ offset: page * limit, limit })`

### Пустое состояние

- Если `documents.length === 0`:
  - Иконка пустой папки по центру (`64px`, `color: var(--color-text-muted)`)
  - «Документы не найдены» — `font-size: 16px`, `color: var(--color-text-secondary)`, `margin-top: 16px`
  - «Загрузите первый документ» — `font-size: 14px`, `color: var(--color-text-muted)`

### Форматирование

```javascript
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' Б'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(0) + ' КБ'
  return (bytes / (1024 * 1024)).toFixed(1) + ' МБ'
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric'
  })
}
```

## Критерии готовности

- Таблица с 6 колонками и корректным форматированием
- Статус-бейджи с правильными цветами
- Пагинация с навигацией по страницам
- Удаление документа с подтверждением
- Пустое состояние при отсутствии документов
- Hover-эффекты на строках и кнопках
