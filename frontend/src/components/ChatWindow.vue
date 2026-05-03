<template>
  <div class="chat-window" ref="containerRef" @scroll="handleScroll">
    <!-- Loading skeleton -->
    <div v-if="chatStore.isLoadingMessages" class="loading-skeleton">
      <div class="skeleton-row short" />
      <div class="skeleton-row long" />
      <div class="skeleton-row medium" />
      <div class="skeleton-row short" />
    </div>

    <template v-else>
      <MessageBubble
        v-for="msg in chatStore.messages"
        :key="msg.id"
        :message="msg"
        :is-streaming="chatStore.isStreaming && msg === chatStore.messages[chatStore.messages.length - 1] && msg.role === 'assistant'"
        @open-source="(e) => $emit('open-source', e)"
        @feedback="(e) => $emit('feedback', e)"
      />
    </template>

    <!-- Scroll to bottom button -->
    <button
      v-if="showScrollButton"
      class="scroll-to-bottom"
      @click="scrollToBottom(true)"
    >
      ↓
    </button>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { useChatStore } from '../stores/chat.js'
import MessageBubble from './MessageBubble.vue'

const chatStore = useChatStore()

defineEmits(['open-source', 'feedback'])

const containerRef = ref(null)
const userScrolledUp = ref(false)
const showScrollButton = ref(false)

function handleScroll() {
  if (!containerRef.value) return
  const { scrollTop, scrollHeight, clientHeight } = containerRef.value
  const distanceFromBottom = scrollHeight - scrollTop - clientHeight
  userScrolledUp.value = distanceFromBottom > 100
  showScrollButton.value = distanceFromBottom > 200
}

function scrollToBottom(force = false) {
  if (userScrolledUp.value && !force) return
  nextTick(() => {
    if (containerRef.value) {
      containerRef.value.scrollTo({
        top: containerRef.value.scrollHeight,
        behavior: 'smooth',
      })
    }
    showScrollButton.value = false
    userScrolledUp.value = false
  })
}

watch(() => chatStore.messages.length, () => {
  scrollToBottom()
})

watch(
  () => {
    const msgs = chatStore.messages
    const last = msgs[msgs.length - 1]
    return last?.role === 'assistant' ? last.content : null
  },
  () => {
    scrollToBottom()
  },
)

watch(
  () => chatStore.isLoadingMessages,
  (loading) => {
    if (!loading) {
      nextTick(() => {
        if (containerRef.value) {
          containerRef.value.scrollTop = containerRef.value.scrollHeight
        }
      })
    }
  },
)

onMounted(() => {
  if (containerRef.value) {
    containerRef.value.scrollTop = containerRef.value.scrollHeight
  }
})
</script>

<style scoped>
.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  scroll-behavior: smooth;
  position: relative;
}

/* Loading skeleton */
.loading-skeleton {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px 0;
}

.skeleton-row {
  height: 48px;
  border-radius: var(--radius-md);
  background: linear-gradient(
    90deg,
    var(--color-bg-surface) 25%,
    var(--color-bg-surface-hover) 50%,
    var(--color-bg-surface) 75%
  );
  background-size: 200px 100%;
  animation: skeleton 1.5s ease-in-out infinite;
}

.skeleton-row.short { width: 40%; }
.skeleton-row.medium { width: 60%; align-self: flex-end; }
.skeleton-row.long { width: 75%; }

/* Scroll to bottom */
.scroll-to-bottom {
  position: sticky;
  bottom: 16px;
  align-self: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-bg-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  backdrop-filter: blur(10px);
  z-index: 5;
}

.scroll-to-bottom:hover {
  background: var(--color-bg-surface-hover);
  box-shadow: var(--shadow-glow);
}
</style>
