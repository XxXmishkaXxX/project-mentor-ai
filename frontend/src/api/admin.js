import { request } from './client.js'

export function getDocuments() {
  return request('/admin/documents')
}

export function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request('/admin/documents', {
    method: 'POST',
    body: formData,
  })
}

export function deleteDocument(documentId) {
  return request(`/admin/documents/${documentId}`, { method: 'DELETE' })
}

export function reindexDocument(documentId) {
  return request(`/admin/documents/${documentId}/reindex`, { method: 'POST' })
}
