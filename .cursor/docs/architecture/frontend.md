# Frontend: Vue 3 + Vite

## Дизайн и визуал

- **Тема**: тёмная «космическая» тема с анимированным Canvas-фоном (частицы + линии)
- **Подробное описание страниц**: [frontend_pages.md](frontend_pages.md) — цвета, компоненты, поведение, API
- **Референс дизайна**: `20725313-3a41-4e4f-8344-c3863c5c6dd9.png`

## Стек

- **Vue 3** (Composition API)
- **Vite** — сборщик
- **Pinia** — state management
- **Vue Router** — роутинг с navigation guards
- **fetch API** — HTTP-клиент (с SSE через ReadableStream)
- **marked** + **DOMPurify** — рендер Markdown в ответах ассистента

## Структура

```
frontend/
├── public/
├── src/
│   ├── api/
│   │   ├── client.js              # fetch instance с credentials: 'include'
│   │   ├── auth.js                # login, register, logout, getMe
│   │   ├── chat.js                # getChats, createChat, sendMessage (SSE)
│   │   └── admin.js               # getDocuments, uploadDocument, deleteDocument
│   ├── stores/
│   │   ├── auth.js                # user, isAuthenticated, login/logout
│   │   ├── chat.js                # chats, currentChat, messages, streaming
│   │   └── admin.js               # documents, upload/delete
│   ├── pages/
│   │   ├── LoginPage.vue
│   │   ├── RegisterPage.vue
│   │   ├── ChatPage.vue           # Основная страница
│   │   └── AdminPage.vue
│   ├── components/
│   │   ├── ChatSidebar.vue        # Список чатов + "новый чат"
│   │   ├── ChatWindow.vue         # Сообщения + автоскролл
│   │   ├── MessageBubble.vue      # Сообщение user/assistant
│   │   ├── SourcesPanel.vue       # Сворачиваемые источники
│   │   ├── FeedbackButtons.vue    # Thumbs up/down
│   │   ├── ChatInput.vue          # Textarea + отправка
│   │   ├── ExampleQuestions.vue   # Подсказки на пустом чате
│   │   ├── DocumentUpload.vue     # Форма загрузки файла
│   │   └── DocumentList.vue       # Таблица документов
│   ├── router/
│   │   └── index.js
│   ├── App.vue
│   └── main.js
├── index.html
├── package.json
└── vite.config.js
```

## Роутинг

| Путь | Компонент | Auth | Описание |
|------|-----------|------|----------|
| /login | LoginPage | - | Вход |
| /register | RegisterPage | - | Регистрация |
| / | redirect -> /chat | required | - |
| /chat | ChatPage | required | Новый чат |
| /chat/:id | ChatPage | required | Существующий чат |
| /admin | AdminPage | admin | Управление документами |

Navigation guards:

- Неавторизованный на защищённых маршрутах -> /login
- Не-admin на /admin -> /chat

## Pinia Stores

**authStore**: `user`, `isAuthenticated` | actions: `login()`, `register()`, `logout()`, `fetchMe()`

**chatStore**: `chats`, `currentChatId`, `messages`, `isStreaming` | actions: `fetchChats()`, `createChat()`, `deleteChat()`, `sendMessage()`, `fetchMessages()`

**adminStore**: `documents`, `isUploading` | actions: `fetchDocuments()`, `uploadDocument()`, `deleteDocument()`, `reindexDocument()`

## SSE-стриминг (POST через fetch + ReadableStream)

```javascript
const response = await fetch(`/api/chats/${chatId}/messages`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ content: question })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const chunk = decoder.decode(value);
  // parse SSE events: token, sources, done
}
```

## Vite Proxy

В dev-режиме Vite проксирует /api на backend (localhost:8000):

```javascript
// vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true }
    }
  }
});
```

## Запуск

```bash
cd frontend
npm install
npm run dev
```
