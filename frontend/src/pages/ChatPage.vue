<template>
  <div class="chat-layout">
    <ChatSidebar
      @new-chat="handleNewChat"
      @select-chat="handleSelectChat"
      @logout="handleLogout"
    />

    <main class="chat-main">
      <header class="chat-header">
        <h2 class="chat-title truncate">{{ chatStore.currentChat?.title || 'Новый чат' }}</h2>
      </header>

      <ExampleQuestions
        v-if="showWelcome"
        @select="handleExampleClick"
      />
      <ChatWindow
        v-else
        @open-source="handleOpenSource"
        @feedback="handleFeedback"
      />

      <ChatInput
        ref="chatInputRef"
        @send="handleSend"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { useChatStore } from '../stores/chat.js'
import ChatSidebar from '../components/ChatSidebar.vue'
import ChatWindow from '../components/ChatWindow.vue'
import ChatInput from '../components/ChatInput.vue'
import ExampleQuestions from '../components/ExampleQuestions.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()
const chatInputRef = ref(null)

const showWelcome = computed(() => {
  return chatStore.messages.length === 0 && !chatStore.isLoadingMessages
})

watch(
  () => route.params.id,
  async (newId) => {
    if (newId) {
      if (newId === chatStore.currentChatId) return
      try {
        await chatStore.selectChat(newId)
      } catch (err) {
        if (err.status === 404) {
          router.replace('/chat')
        }
      }
    } else if (chatStore.currentChatId) {
      chatStore.clearCurrentChat()
    }
  },
)

async function handleSend(content) {
  let chatId = chatStore.currentChatId

  if (!chatId) {
    const chat = await chatStore.createChat()
    chatId = chat.id
    router.replace(`/chat/${chatId}`)
  }

  await chatStore.sendMessage(content)
  await chatStore.fetchChats()
}

async function handleExampleClick(question) {
  await handleSend(question)
}

function handleNewChat() {
  chatStore.clearCurrentChat()
  router.push('/chat')
}

function handleSelectChat(chatId) {
  router.push(`/chat/${chatId}`)
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

function handleOpenSource(event) {
  // Future: open source details panel
  console.log('Open source:', event)
}

function handleFeedback(event) {
  // Future: send feedback to API
  console.log('Feedback:', event)
}

onMounted(async () => {
  await chatStore.fetchChats()
  if (route.params.id) {
    try {
      await chatStore.selectChat(route.params.id)
    } catch (err) {
      if (err.status === 404) {
        router.replace('/chat')
      }
    }
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
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid var(--color-border);
  background: rgba(13, 16, 51, 0.5);
  backdrop-filter: blur(10px);
  flex-shrink: 0;
}

.chat-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
}
</style>
