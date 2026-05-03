<template>
  <div class="chat-layout">
    <aside class="chat-sidebar">
      <div class="sidebar-top">
        <button class="btn-new-chat" @click="handleNewChat">
          + Новый чат
        </button>
        <div class="search-wrapper">
          <span class="search-icon">🔍</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск чатов..."
            class="search-input"
          >
        </div>
      </div>

      <div class="chat-list">
        <template v-for="group in filteredChatGroups" :key="group.label">
          <div class="chat-group-label">{{ group.label }}</div>
          <div
            v-for="chat in group.chats"
            :key="chat.id"
            class="chat-item"
            :class="{ active: chat.id === chatStore.currentChatId }"
            @click="openChat(chat.id)"
          >
            <span class="chat-item-title truncate">{{ chat.title || 'Новый чат' }}</span>
            <button
              class="chat-item-delete"
              @click.stop="handleDeleteChat(chat.id)"
            >🗑</button>
          </div>
        </template>
        <div v-if="!chatStore.chats.length" class="empty-chats">
          Начните первый диалог!
        </div>
      </div>

      <div class="sidebar-profile">
        <div class="profile-avatar">
          {{ authStore.user?.username?.charAt(0)?.toUpperCase() || '?' }}
        </div>
        <div class="profile-info">
          <span class="profile-name truncate">{{ authStore.user?.username }}</span>
          <span class="profile-role">{{ authStore.isAdmin ? 'Админ' : 'Студент' }}</span>
        </div>
        <button class="btn-logout" @click="handleLogout">↪</button>
      </div>
    </aside>

    <main class="chat-main">
      <header class="chat-header">
        <h2>{{ chatStore.currentChat?.title || 'Новый чат' }}</h2>
      </header>

      <div class="chat-messages" ref="messagesRef">
        <div v-if="!chatStore.messages.length" class="welcome-screen">
          <div class="welcome-icon">💬</div>
          <h2>Привет! Я ваш проектный ассистент</h2>
          <p>Задавайте вопросы по управлению проектами, Agile, Scrum, DevOps и другим практикам.</p>
          <span class="examples-label">Примеры вопросов:</span>
          <div class="example-grid">
            <button
              v-for="q in exampleQuestions"
              :key="q"
              class="example-card"
              @click="handleExampleClick(q)"
            >
              <span>{{ q }}</span>
              <span class="example-arrow">→</span>
            </button>
          </div>
        </div>

        <template v-else>
          <div
            v-for="msg in chatStore.messages"
            :key="msg.id"
            class="message"
            :class="msg.role"
          >
            <div v-if="msg.role === 'assistant'" class="message-avatar">🤖</div>
            <div class="message-bubble">
              <div v-html="msg.role === 'assistant' ? renderMarkdown(msg.content) : msg.content" />
            </div>
          </div>

          <div v-if="chatStore.isStreaming && !lastAssistantContent" class="message assistant">
            <div class="message-avatar">🤖</div>
            <div class="message-bubble typing-indicator">
              <span class="dot" /><span class="dot" /><span class="dot" />
            </div>
          </div>
        </template>
      </div>

      <div class="chat-input-area">
        <div class="input-wrapper">
          <textarea
            v-model="messageText"
            placeholder="Задайте вопрос..."
            rows="1"
            @keydown.enter.exact.prevent="handleSend"
            @input="autoResize"
            ref="textareaRef"
          />
          <button
            class="btn-send"
            :disabled="!messageText.trim() || chatStore.isStreaming"
            @click="handleSend"
          >
            ↑
          </button>
        </div>
        <span class="input-hint">Shift + Enter для новой строки</span>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { useChatStore } from '../stores/chat.js'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

const messageText = ref('')
const searchQuery = ref('')
const messagesRef = ref(null)
const textareaRef = ref(null)

const exampleQuestions = [
  'Как правильно составить ТЗ?',
  'Какие этапы у Scrum?',
  'Как распределить роли в команде?',
  'Что такое Kanban?',
]

const lastAssistantContent = computed(() => {
  const msgs = chatStore.messages
  const last = msgs[msgs.length - 1]
  return last?.role === 'assistant' ? last.content : ''
})

function renderMarkdown(text) {
  if (!text) return ''
  return DOMPurify.sanitize(marked.parse(text))
}

function groupChatsByDate(chats) {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  const groups = { today: [], yesterday: [], earlier: [] }

  for (const chat of chats) {
    const d = new Date(chat.created_at)
    if (d >= today) groups.today.push(chat)
    else if (d >= yesterday) groups.yesterday.push(chat)
    else groups.earlier.push(chat)
  }

  const result = []
  if (groups.today.length) result.push({ label: 'Сегодня', chats: groups.today })
  if (groups.yesterday.length) result.push({ label: 'Вчера', chats: groups.yesterday })
  if (groups.earlier.length) result.push({ label: 'Ранее', chats: groups.earlier })
  return result
}

const filteredChatGroups = computed(() => {
  let chats = chatStore.chats
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    chats = chats.filter(c =>
      (c.title || '').toLowerCase().includes(q)
    )
  }
  return groupChatsByDate(chats)
})

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

watch(() => chatStore.messages.length, scrollToBottom)
watch(() => chatStore.messages[chatStore.messages.length - 1]?.content, scrollToBottom)

async function handleSend() {
  const text = messageText.value.trim()
  if (!text || chatStore.isStreaming) return

  if (!chatStore.currentChatId) {
    await chatStore.createChat()
    router.replace(`/chat/${chatStore.currentChatId}`)
  }

  messageText.value = ''
  if (textareaRef.value) textareaRef.value.style.height = 'auto'
  await chatStore.sendMessage(text)
  await chatStore.fetchChats()
}

async function handleExampleClick(question) {
  messageText.value = question
  await handleSend()
}

async function handleNewChat() {
  chatStore.setCurrentChat(null)
  chatStore.messages = []
  router.push('/chat')
}

async function openChat(chatId) {
  router.push(`/chat/${chatId}`)
  await chatStore.fetchMessages(chatId)
}

async function handleDeleteChat(chatId) {
  if (!confirm('Удалить чат?')) return
  await chatStore.deleteChat(chatId)
  if (chatStore.currentChatId === null) {
    router.push('/chat')
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

function autoResize(event) {
  const el = event.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 200) + 'px'
}

onMounted(async () => {
  await chatStore.fetchChats()
  if (route.params.id) {
    await chatStore.fetchMessages(route.params.id)
  }
})
</script>

<style scoped>
.chat-layout {
  position: relative;
  z-index: 1;
  display: flex;
  height: 100vh;
}

/* Sidebar */
.chat-sidebar {
  width: 280px;
  min-width: 280px;
  background: rgba(13, 16, 51, 0.9);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.sidebar-top {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-new-chat {
  width: 100%;
  height: 42px;
  background: var(--color-accent-gradient);
  color: #fff;
  font-weight: 600;
  border-radius: var(--radius-md);
}

.btn-new-chat:hover {
  box-shadow: var(--shadow-glow);
}

.search-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
}

.search-input {
  padding-left: 36px;
  height: 38px;
  font-size: 13px;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.chat-group-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  padding: 8px 12px 4px;
  letter-spacing: 0.5px;
}

.chat-item {
  padding: 10px 16px;
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: background var(--transition-base);
}

.chat-item:hover {
  background: var(--color-bg-surface-hover);
}

.chat-item.active {
  background: var(--color-bg-surface);
  border-left: 3px solid var(--color-accent-primary);
}

.chat-item-title {
  font-size: var(--font-size-base);
  flex: 1;
  min-width: 0;
}

.chat-item-delete {
  background: none;
  font-size: 14px;
  opacity: 0;
  padding: 4px;
}

.chat-item:hover .chat-item-delete {
  opacity: 0.6;
}

.chat-item-delete:hover {
  opacity: 1 !important;
}

.empty-chats {
  text-align: center;
  color: var(--color-text-muted);
  padding: 32px 16px;
  font-size: var(--font-size-base);
}

.sidebar-profile {
  padding: 16px;
  border-top: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  gap: 10px;
}

.profile-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: var(--color-accent-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: var(--font-size-base);
  flex-shrink: 0;
}

.profile-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.profile-name {
  font-size: var(--font-size-base);
  font-weight: 500;
}

.profile-role {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.btn-logout {
  background: none;
  color: var(--color-text-muted);
  font-size: 18px;
  padding: 4px;
}

.btn-logout:hover {
  color: var(--color-text-primary);
}

/* Main */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid var(--color-border);
  background: rgba(13, 16, 51, 0.5);
  backdrop-filter: blur(10px);
}

.chat-header h2 {
  font-size: var(--font-size-md);
  font-weight: 600;
}

/* Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 12px;
}

.welcome-icon {
  font-size: 80px;
  filter: drop-shadow(0 0 20px rgba(108, 92, 231, 0.4));
}

.welcome-screen h2 {
  font-size: var(--font-size-xl);
}

.welcome-screen p {
  color: var(--color-text-secondary);
  max-width: 480px;
}

.examples-label {
  color: var(--color-text-secondary);
  font-size: 13px;
  margin-top: 8px;
}

.example-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 8px;
  max-width: 540px;
  width: 100%;
}

.example-card {
  background: rgba(18, 20, 56, 0.6);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 14px 18px;
  color: var(--color-text-primary);
  text-align: left;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: var(--font-size-base);
}

.example-card:hover {
  border-color: var(--color-accent-primary);
  background: rgba(108, 92, 231, 0.1);
}

.example-arrow {
  color: var(--color-accent-primary);
  flex-shrink: 0;
}

/* Messages */
.message {
  display: flex;
  gap: 10px;
  animation: fadeInUp var(--transition-slow) ease;
}

.message.user {
  justify-content: flex-end;
}

.message.user .message-bubble {
  background: var(--color-user-bubble);
  border-radius: 16px 16px 4px 16px;
  max-width: 70%;
}

.message.assistant .message-bubble {
  background: var(--color-assistant-bubble);
  border: 1px solid var(--color-border);
  border-radius: 16px 16px 16px 4px;
  max-width: 80%;
}

.message-avatar {
  width: 32px;
  height: 32px;
  font-size: 20px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-bubble {
  padding: 12px 18px;
  line-height: 1.5;
  word-break: break-word;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 16px 20px;
}

.typing-indicator .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-text-muted);
  animation: pulse 1.4s ease-in-out infinite;
}

.typing-indicator .dot:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator .dot:nth-child(3) { animation-delay: 0.4s; }

/* Input */
.chat-input-area {
  padding: 16px 24px;
  background: rgba(13, 16, 51, 0.7);
  backdrop-filter: blur(10px);
}

.input-wrapper {
  position: relative;
}

.input-wrapper textarea {
  width: 100%;
  min-height: 44px;
  max-height: 200px;
  padding: 12px 50px 12px 16px;
  border-radius: var(--radius-lg);
  resize: none;
  overflow-y: auto;
}

.btn-send {
  position: absolute;
  right: 8px;
  bottom: 6px;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: var(--color-accent-gradient);
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-send:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-send:hover:not(:disabled) {
  box-shadow: var(--shadow-glow);
}

.input-hint {
  display: block;
  text-align: center;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin-top: 6px;
}
</style>
