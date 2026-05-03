import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as adminApi from '../api/admin.js'

export const useAdminStore = defineStore('admin', () => {
  const documents = ref([])
  const isUploading = ref(false)
  const isLoading = ref(false)

  async function fetchDocuments() {
    isLoading.value = true
    try {
      documents.value = await adminApi.getDocuments()
    } finally {
      isLoading.value = false
    }
  }

  async function uploadDocument(file) {
    isUploading.value = true
    try {
      const doc = await adminApi.uploadDocument(file)
      documents.value.unshift(doc)
      return doc
    } finally {
      isUploading.value = false
    }
  }

  async function deleteDocument(documentId) {
    await adminApi.deleteDocument(documentId)
    documents.value = documents.value.filter(d => d.id !== documentId)
  }

  async function reindexDocument(documentId) {
    await adminApi.reindexDocument(documentId)
  }

  return {
    documents,
    isUploading,
    isLoading,
    fetchDocuments,
    uploadDocument,
    deleteDocument,
    reindexDocument,
  }
})
