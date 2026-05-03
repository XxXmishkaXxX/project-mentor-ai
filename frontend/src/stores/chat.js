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

  async function createChat(title = null) {
    const chat = await chatApi.createChat(title)
    chats.value.unshift(chat)
    currentChatId.value = chat.id
    messages.value = []
    return chat
  }

  async function deleteChat(chatId) {
    await chatApi.deleteChat(chatId)
    chats.value = chats.value.filter(c => c.id !== chatId)
    if (currentChatId.value === chatId) {
      currentChatId.value = null
      messages.value = []
    }
  }

  async function fetchMessages(chatId) {
    isLoadingMessages.value = true
    try {
      messages.value = await chatApi.getMessages(chatId)
      currentChatId.value = chatId
    } finally {
      isLoadingMessages.value = false
    }
  }

  async function sendMessage(content) {
    if (!currentChatId.value || isStreaming.value) return

    const userMessage = {
      id: `temp-${Date.now()}`,
      chat_id: currentChatId.value,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }
    messages.value.push(userMessage)

    const assistantMessage = {
      id: `temp-assistant-${Date.now()}`,
      chat_id: currentChatId.value,
      role: 'assistant',
      content: '',
      sources: [],
      created_at: new Date().toISOString(),
    }
    messages.value.push(assistantMessage)

    isStreaming.value = true
    try {
      const response = await chatApi.sendMessage(currentChatId.value, content)
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6).trim()
          if (!data) continue

          try {
            const event = JSON.parse(data)
            if (event.type === 'token') {
              assistantMessage.content += event.content
            } else if (event.type === 'sources') {
              assistantMessage.sources = event.sources
            } else if (event.type === 'done') {
              if (event.message_id) {
                assistantMessage.id = event.message_id
              }
              if (event.user_message_id) {
                userMessage.id = event.user_message_id
              }
            }
          } catch {
            // skip malformed events
          }
        }
      }
    } finally {
      isStreaming.value = false
    }
  }

  function setCurrentChat(chatId) {
    currentChatId.value = chatId
  }

  return {
    chats,
    currentChatId,
    currentChat,
    messages,
    isStreaming,
    isLoadingChats,
    isLoadingMessages,
    fetchChats,
    createChat,
    deleteChat,
    fetchMessages,
    sendMessage,
    setCurrentChat,
  }
})
