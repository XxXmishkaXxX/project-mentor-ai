# FE-002: Proxy API в Vite

**Приоритет**: Блокирующий
**Этап**: 0
**US**: -
**Зависимости**: FE-001
**Статус**: не начата

## Описание

Настройка прокси в dev-режиме Vite для запросов к backend без CORS-проблем и с сохранением cookie (сессии). Все запросы с фронта идут на `/api`, а Vite перенаправляет их на локальный backend.

## Файлы

- `frontend/vite.config.js` — секция `server.proxy` для `/api`

## Реализация

В `vite.config.js` добавить:

```js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
},
```

Убедиться, что относительные URL вида `/api/...` в dev попадают на backend. Cookie должны пробрасываться при `credentials: 'include'` на стороне клиента (см. FE-003).

## Критерии готовности

- Запросы к `/api` проксируются на `http://localhost:8000`
- Cookie передаются между браузером и backend в dev-режиме
