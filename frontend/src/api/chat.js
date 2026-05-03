import { request, streamRequest } from './client.js'

export function getChats() {
  return request('/chats')
}

export function createChat(title = null) {
  return request('/chats', {
    method: 'POST',
    body: { title },
  })
}

export function deleteChat(chatId) {
  return request(`/chats/${chatId}`, { method: 'DELETE' })
}

export function getMessages(chatId) {
  return request(`/chats/${chatId}/messages`)
}

export function sendMessage(chatId, content) {
  return streamRequest(`/chats/${chatId}/messages`, { content })
}
