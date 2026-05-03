import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as chatApi from '../api/chat.js'

export const useChatStore = defineStore('chat', () => {
  const chats = ref([])
  const currentChatId = ref(null)
  const messages = ref([])
  const isStreaming = ref(false)
  const isLoadingChats = ref(false)
  const isLoadingMessages = ref(false)
  const messagesTotal = ref(0)

  const currentChat = computed(() =>
    chats.value.find(c => c.id === currentChatId.value) || null
  )

  async function fetchChats() {
    isLoadingChats.value = true
    try {
      chats.value = await chatApi.getChats()
    } finally {
      isLoadingChats.value = false
    }
  }

  async function createChat() {
    const chat = await chatApi.createChat()
    chats.value.unshift(chat)
    currentChatId.value = chat.id
    messages.value = []
    messagesTotal.value = 0
    return chat
  }

  async function deleteChat(chatId) {
    await chatApi.deleteChat(chatId)
    chats.value = chats.value.filter(c => c.id !== chatId)
    if (currentChatId.value === chatId) {
      currentChatId.value = null
      messages.value = []
      messagesTotal.value = 0
    }
  }

  async function selectChat(chatId) {
    currentChatId.value = chatId
    await fetchMessages(chatId)
  }

  async function fetchMessages(chatId, offset = 0, limit = 50) {
    isLoadingMessages.value = true
    try {
      const data = await chatApi.getMessages(chatId, offset, limit)
      messages.value = data.messages || []
      messagesTotal.value = data.total || 0
      currentChatId.value = chatId
    } finally {
      isLoadingMessages.value = false
    }
  }

  function clearCurrentChat() {
    currentChatId.value = null
    messages.value = []
    messagesTotal.value = 0
  }

  async function sendMessage(content) {
    if (!currentChatId.value || isStreaming.value) return

    const userMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      sources: null,
      created_at: new Date().toISOString(),
    }
    messages.value.push(userMessage)

    messages.value.push({
      id: `temp-assistant-${Date.now()}`,
      role: 'assistant',
      content: '',
      sources: null,
      created_at: new Date().toISOString(),
    })

    const assistantMessage = messages.value[messages.value.length - 1]

    isStreaming.value = true
    try {
      const response = await chatApi.sendMessageStream(currentChatId.value, content)
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      let eventType = null
      let dataLines = []

      function dispatchEvent() {
        if (!eventType || dataLines.length === 0) {
          eventType = null
          dataLines = []
          return
        }
        const data = dataLines.join('\n')
        dataLines = []

        if (eventType === 'token') {
          assistantMessage.content += data
        } else if (eventType === 'sources') {
          try {
            const parsed = JSON.parse(data)
            assistantMessage.sources = Array.isArray(parsed) ? parsed : parsed.sources || []
          } catch { /* skip malformed sources */ }
        } else if (eventType === 'done') {
          if (data) {
            try {
              const parsed = JSON.parse(data)
              if (parsed.message_id) assistantMessage.id = parsed.message_id
            } catch { /* done without JSON payload */ }
          }
        } else if (eventType === 'error' || eventType === 'no_data') {
          assistantMessage.content += data || ''
        }

        eventType = null
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          const trimmed = line.trim()

          if (!trimmed) {
            dispatchEvent()
            continue
          }

          if (trimmed.startsWith('event:')) {
            eventType = trimmed.slice(6).trim()
            continue
          }

          if (trimmed.startsWith('data:')) {
            dataLines.push(trimmed.slice(5).trimStart())
          }
        }
      }
      dispatchEvent()
    } catch (err) {
      const lastMsg = messages.value[messages.value.length - 1]
      if (lastMsg?.role === 'assistant' && !lastMsg.content) {
        lastMsg.content = 'Произошла ошибка при получении ответа. Попробуйте ещё раз.'
      }
      console.error('Stream error:', err)
    } finally {
      isStreaming.value = false
    }
  }

  return {
    chats,
    currentChatId,
    currentChat,
    messages,
    messagesTotal,
    isStreaming,
    isLoadingChats,
    isLoadingMessages,
    fetchChats,
    createChat,
    deleteChat,
    selectChat,
    fetchMessages,
    clearCurrentChat,
    sendMessage,
  }
})
