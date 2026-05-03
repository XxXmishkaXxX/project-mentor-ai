import { request, streamRequest } from './client.js'

export function getChats() {
  return request('/chats/')
}

export function createChat() {
  return request('/chats/', { method: 'POST' })
}

export function getChat(chatId) {
  return request(`/chats/${chatId}`)
}

export function deleteChat(chatId) {
  return request(`/chats/${chatId}`, { method: 'DELETE' })
}

export async function getMessages(chatId, offset = 0, limit = 50) {
  const data = await request(`/chats/${chatId}/messages?offset=${offset}&limit=${limit}`)
  return data
}

export function sendMessageStream(chatId, content) {
  return streamRequest(`/chats/${chatId}/messages`, { content })
}
