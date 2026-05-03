<template>
  <div class="chat-input-area">
    <div class="input-wrapper">
      <textarea
        ref="textareaRef"
        v-model="text"
        placeholder="Задайте вопрос..."
        rows="1"
        :disabled="chatStore.isStreaming"
        @keydown="handleKeydown"
        @input="autoResize"
      />
      <button
        class="btn-send"
        :disabled="!canSend"
        @click="handleSend"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="19" x2="12" y2="5" />
          <polyline points="5 12 12 5 19 12" />
        </svg>
      </button>
    </div>
    <span class="input-hint">Shift + Enter для новой строки</span>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useChatStore } from '../stores/chat.js'

const emit = defineEmits(['send'])
const chatStore = useChatStore()

const text = ref('')
const textareaRef = ref(null)

const canSend = computed(() => {
  return text.value.trim().length > 0 && !chatStore.isStreaming
})

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function handleSend() {
  const content = text.value.trim()
  if (!content || chatStore.isStreaming) return
  text.value = ''
  resetTextareaHeight()
  emit('send', content)
}

function autoResize(event) {
  const el = event.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 200) + 'px'
}

function resetTextareaHeight() {
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  })
}

function focus() {
  nextTick(() => {
    textareaRef.value?.focus()
  })
}

watch(() => chatStore.isStreaming, (streaming, wasStreaming) => {
  if (wasStreaming && !streaming) {
    focus()
  }
})

onMounted(() => {
  focus()
})

defineExpose({ focus })
</script>

<style scoped>
.chat-input-area {
  padding: 16px 24px;
  background: rgba(13, 16, 51, 0.7);
  backdrop-filter: blur(10px);
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}

.input-wrapper {
  position: relative;
}

.input-wrapper textarea {
  width: 100%;
  min-height: 44px;
  max-height: 200px;
  padding: 12px 56px 12px 16px;
  border-radius: 12px;
  resize: none;
  overflow-y: auto;
}

.input-wrapper textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-send {
  position: absolute;
  right: 8px;
  bottom: 6px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-accent-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
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
