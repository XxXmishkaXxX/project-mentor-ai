<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="admin-logo">
        <div class="logo-icon">🛡️</div>
        <h1 class="logo-title">Проектный Ассистент</h1>
      </div>

      <nav class="admin-nav">
        <a class="nav-item active">
          <span class="nav-icon">📄</span>
          <span>Документы</span>
        </a>
        <a class="nav-item disabled">
          <span class="nav-icon">📊</span>
          <span>Статистика</span>
        </a>
        <a class="nav-item disabled">
          <span class="nav-icon">👥</span>
          <span>Пользователи</span>
        </a>
        <a class="nav-item disabled">
          <span class="nav-icon">⚙️</span>
          <span>Настройки</span>
        </a>
      </nav>

      <div class="admin-sidebar-bottom">
        <router-link to="/chat" class="back-link">← Вернуться к чату</router-link>
      </div>
    </aside>

    <main class="admin-content">
      <header class="admin-header">
        <h2>Документы</h2>
        <button class="btn-upload" @click="triggerUpload">
          + Загрузить документ
        </button>
        <input
          ref="fileInputRef"
          type="file"
          hidden
          @change="handleFileUpload"
        >
      </header>

      <div class="documents-section">
        <div v-if="adminStore.isLoading" class="loading-state">
          <div class="spinner" />
          <span>Загрузка документов...</span>
        </div>

        <div v-else-if="!adminStore.documents.length" class="empty-state">
          <span class="empty-icon">📁</span>
          <p>Загрузите первый документ</p>
        </div>

        <table v-else class="documents-table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Статус</th>
              <th>Дата добавления</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="doc in adminStore.documents" :key="doc.id">
              <td>{{ doc.filename || doc.title }}</td>
              <td>
                <span class="status-badge" :class="doc.status">
                  {{ statusLabels[doc.status] || doc.status }}
                </span>
              </td>
              <td class="text-muted">{{ formatDate(doc.created_at) }}</td>
              <td>
                <button class="btn-icon btn-delete" @click="handleDelete(doc.id)">🗑</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '../stores/admin.js'

const adminStore = useAdminStore()
const fileInputRef = ref(null)

const statusLabels = {
  indexed: 'Проиндексирован',
  processing: 'В обработке',
  error: 'Ошибка',
  pending: 'Ожидание',
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

function triggerUpload() {
  fileInputRef.value?.click()
}

async function handleFileUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return
  await adminStore.uploadDocument(file)
  event.target.value = ''
}

async function handleDelete(docId) {
  if (!confirm('Удалить документ?')) return
  await adminStore.deleteDocument(docId)
}

onMounted(() => {
  adminStore.fetchDocuments()
})
</script>

<style scoped>
.admin-layout {
  position: relative;
  z-index: 1;
  display: flex;
  height: 100vh;
}

.admin-sidebar {
  width: 250px;
  min-width: 250px;
  background: rgba(13, 16, 51, 0.9);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: 20px 0;
}

.admin-logo {
  text-align: center;
  padding: 0 16px 24px;
  border-bottom: 1px solid var(--color-border);
}

.admin-logo .logo-icon {
  font-size: 32px;
  margin-bottom: 4px;
}

.admin-logo .logo-title {
  font-size: 15px;
  font-weight: 700;
}

.admin-nav {
  flex: 1;
  padding: 16px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  cursor: pointer;
  text-decoration: none;
  transition: all var(--transition-base);
}

.nav-item:hover:not(.disabled) {
  background: var(--color-bg-surface-hover);
  color: var(--color-text-primary);
  text-decoration: none;
}

.nav-item.active {
  background: var(--color-bg-surface);
  color: var(--color-text-primary);
  border-left: 3px solid var(--color-accent-primary);
}

.nav-item.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.nav-icon {
  font-size: 16px;
}

.admin-sidebar-bottom {
  padding: 16px;
  border-top: 1px solid var(--color-border);
}

.back-link {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.admin-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow-y: auto;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 32px;
  border-bottom: 1px solid var(--color-border);
}

.admin-header h2 {
  font-size: var(--font-size-lg);
}

.btn-upload {
  background: var(--color-accent-green);
  color: #fff;
  font-weight: 600;
  padding: 10px 20px;
  border-radius: var(--radius-md);
}

.btn-upload:hover {
  filter: brightness(1.1);
}

.documents-section {
  flex: 1;
  padding: 24px 32px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 64px 0;
  color: var(--color-text-muted);
}

.empty-icon {
  font-size: 48px;
}

.documents-table {
  width: 100%;
  border-collapse: collapse;
}

.documents-table th {
  text-align: left;
  padding: 12px 16px;
  font-weight: 600;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--color-border);
}

.documents-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
}

.documents-table tr:hover {
  background: var(--color-bg-surface-hover);
}

.text-muted {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.status-badge.indexed {
  background: rgba(0, 214, 143, 0.15);
  color: var(--color-accent-green);
}

.status-badge.processing {
  background: rgba(255, 165, 2, 0.15);
  color: var(--color-accent-yellow);
}

.status-badge.error {
  background: rgba(255, 71, 87, 0.15);
  color: var(--color-accent-red);
}

.status-badge.pending {
  background: rgba(91, 91, 123, 0.15);
  color: var(--color-text-muted);
}

.btn-icon {
  background: none;
  font-size: 16px;
  padding: 6px;
  border-radius: var(--radius-sm);
}

.btn-delete:hover {
  background: rgba(255, 71, 87, 0.15);
}
</style>
