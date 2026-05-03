<template>
  <aside class="chat-sidebar">
    <div class="sidebar-top">
      <button class="btn-new-chat" @click="$emit('new-chat')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        Новый чат
      </button>

      <div class="search-wrapper">
        <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Поиск чатов..."
          class="search-input"
        >
      </div>
    </div>

    <div class="chat-list">
      <template v-if="filteredChatGroups.length">
        <template v-for="group in filteredChatGroups" :key="group.label">
          <div class="chat-group-label">{{ group.label }}</div>
          <div
            v-for="chat in group.chats"
            :key="chat.id"
            class="chat-item"
            :class="{ active: chat.id === chatStore.currentChatId }"
            @click="$emit('select-chat', chat.id)"
          >
            <span class="chat-item-title truncate">{{ chat.title || 'Новый чат' }}</span>
            <button
              class="chat-item-delete"
              title="Удалить чат"
              @click.stop="handleDelete(chat.id)"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6" />
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
              </svg>
            </button>
          </div>
        </template>
      </template>
      <div v-else-if="!chatStore.chats.length" class="empty-chats">
        Начните первый диалог!
      </div>
      <div v-else class="empty-chats">
        Ничего не найдено
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
      <button class="btn-logout" title="Выйти" @click="$emit('logout')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" y1="12" x2="9" y2="12" />
        </svg>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useChatStore } from '../stores/chat.js'
import { useAuthStore } from '../stores/auth.js'

const chatStore = useChatStore()
const authStore = useAuthStore()

defineEmits(['new-chat', 'select-chat', 'logout'])

const searchQuery = ref('')

function groupChatsByDate(chats) {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  const groups = { today: [], yesterday: [], earlier: [] }

  for (const chat of chats) {
    const d = new Date(chat.updated_at || chat.created_at)
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

function handleDelete(chatId) {
  if (!confirm('Удалить чат?')) return
  chatStore.deleteChat(chatId)
}
</script>

<style scoped>
.chat-sidebar {
  width: 280px;
  min-width: 280px;
  height: 100vh;
  background: rgba(13, 16, 51, 0.9);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.sidebar-top {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.btn-new-chat {
  width: 100%;
  height: 42px;
  background: var(--color-accent-gradient);
  color: #fff;
  font-weight: 500;
  font-size: var(--font-size-base);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
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
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input {
  padding-left: 36px;
  height: 38px;
  font-size: 13px;
}

/* Chat list */
.chat-list {
  flex: 1;
  overflow-y: auto;
}

.chat-group-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
  padding: 8px 8px 4px;
  margin-top: 8px;
}

.chat-item {
  padding: 10px 12px;
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
  box-shadow: inset 3px 0 0 var(--color-accent-primary);
}

.chat-item-title {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  flex: 1;
  min-width: 0;
}

.chat-item-delete {
  background: none;
  color: var(--color-text-muted);
  opacity: 0;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.chat-item:hover .chat-item-delete {
  opacity: 1;
}

.chat-item-delete:hover {
  color: var(--color-accent-red);
}

.empty-chats {
  text-align: center;
  color: var(--color-text-muted);
  padding: 32px 16px;
  font-size: var(--font-size-base);
}

/* Profile */
.sidebar-profile {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  gap: 12px;
}

.profile-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-accent-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: var(--font-size-base);
  color: #fff;
  flex-shrink: 0;
}

.profile-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.profile-name {
  font-size: 14px;
  font-weight: 500;
}

.profile-role {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.btn-logout {
  background: none;
  color: var(--color-text-muted);
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-logout:hover {
  color: var(--color-text-primary);
}
</style>
