<template>
  <div v-if="message.role !== 'system'" class="message" :class="message.role">
    <div v-if="message.role === 'assistant'" class="message-avatar">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 8V4H8"/>
        <rect width="16" height="12" x="4" y="8" rx="2"/>
        <path d="M2 14h2M20 14h2M15 13v2M9 13v2"/>
      </svg>
    </div>
    <div class="message-content">
      <div class="message-bubble">
        <div v-if="message.role === 'assistant' && isStreaming && !message.content" class="typing-dots">
          <span class="dot" /><span class="dot" /><span class="dot" />
        </div>
        <div
          v-else-if="message.role === 'assistant'"
          class="markdown-body"
          v-html="renderedContent"
        />
        <div v-else>{{ message.content }}</div>

        <div v-if="hasSources" class="sources-block">
          <div class="sources-header">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
            </svg>
            <span>Источники</span>
          </div>
          <ol class="sources-list">
            <li
              v-for="(src, idx) in message.sources"
              :key="idx"
              class="source-item"
              @click="$emit('open-source', { sources: message.sources, index: idx })"
            >
              {{ src.document_title }}
            </li>
          </ol>
        </div>
      </div>

      <div v-if="message.role === 'assistant' && !isStreaming" class="message-actions">
        <button class="action-btn" title="Нравится" @click="$emit('feedback', { messageId: message.id, type: 'like' })">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 10v12M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/></svg>
        </button>
        <button class="action-btn" title="Не нравится" @click="$emit('feedback', { messageId: message.id, type: 'dislike' })">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 14V2M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L14 22h0a3.13 3.13 0 0 1-3-3.88Z"/></svg>
        </button>
        <button class="action-btn" title="Копировать" @click="copyContent">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
        </button>
      </div>

      <div class="message-time">
        {{ formattedTime }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
  isStreaming: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['open-source', 'feedback', 'open-feedback'])

const renderedContent = computed(() => {
  if (!props.message.content) return ''
  return DOMPurify.sanitize(marked.parse(props.message.content))
})

const hasSources = computed(() => {
  return props.message.sources && props.message.sources.length > 0
})

const formattedTime = computed(() => {
  if (!props.message.created_at) return ''
  const d = new Date(props.message.created_at)
  return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
})

async function copyContent() {
  try {
    await navigator.clipboard.writeText(props.message.content)
  } catch {
    // fallback ignored
  }
}
</script>

<style scoped>
.message {
  display: flex;
  gap: 12px;
  animation: fadeInUp var(--transition-slow) ease;
}

.message.user {
  justify-content: flex-end;
}

.message-content {
  max-width: 80%;
  min-width: 0;
}

.message.user .message-content {
  max-width: 70%;
  align-items: flex-end;
  display: flex;
  flex-direction: column;
}

.message-bubble {
  padding: 12px 18px;
  line-height: 1.5;
  word-break: break-word;
}

.message.user .message-bubble {
  background: var(--color-user-bubble);
  color: #ffffff;
  border-radius: 16px 16px 4px 16px;
}

.message.assistant .message-bubble {
  background: var(--color-assistant-bubble);
  border: 1px solid var(--color-border);
  border-radius: 16px 16px 16px 4px;
  padding: 16px 20px;
  color: var(--color-text-primary);
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-bg-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--color-accent-primary);
}

.message-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin-top: 4px;
}

.message.user .message-time {
  text-align: right;
}

/* Markdown styles */
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  font-weight: 600;
  margin: 16px 0 8px;
}

.markdown-body :deep(h1) { font-size: var(--font-size-lg); }
.markdown-body :deep(h2) { font-size: var(--font-size-md); }
.markdown-body :deep(h3) { font-size: var(--font-size-base); }

.markdown-body :deep(ol),
.markdown-body :deep(ul) {
  padding-left: 20px;
  margin: 8px 0;
  list-style: revert;
}

.markdown-body :deep(li) {
  margin: 4px 0;
}

.markdown-body :deep(code) {
  background: rgba(108, 92, 231, 0.15);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
}

.markdown-body :deep(pre > code) {
  display: block;
  background: rgba(0, 0, 0, 0.3);
  padding: 12px 16px;
  border-radius: 8px;
  overflow-x: auto;
}

.markdown-body :deep(pre) {
  margin: 8px 0;
}

.markdown-body :deep(strong) {
  font-weight: 600;
}

.markdown-body :deep(em) {
  font-style: italic;
}

.markdown-body :deep(a) {
  color: var(--color-accent-primary);
}

.markdown-body :deep(p) {
  margin: 8px 0;
}

.markdown-body :deep(p:first-child) {
  margin-top: 0;
}

.markdown-body :deep(p:last-child) {
  margin-bottom: 0;
}

/* Typing dots */
.typing-dots {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
}

.typing-dots .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-text-secondary);
  animation: pulse 1.4s ease-in-out infinite;
}

.typing-dots .dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dots .dot:nth-child(3) { animation-delay: 0.4s; }

/* Sources block */
.sources-block {
  background: rgba(108, 92, 231, 0.08);
  border-radius: var(--radius-md);
  padding: 12px;
  margin-top: 12px;
}

.sources-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.sources-list {
  list-style: decimal;
  padding-left: 20px;
  margin: 0;
}

.source-item {
  font-size: 13px;
  color: var(--color-accent-primary);
  cursor: pointer;
  margin: 4px 0;
}

.source-item:hover {
  text-decoration: underline;
}

/* Action buttons */
.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.action-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  color: var(--color-text-muted);
  border-radius: var(--radius-sm);
  padding: 0;
}

.action-btn:hover {
  color: var(--color-text-secondary);
  background: var(--color-bg-surface-hover);
}
</style>
