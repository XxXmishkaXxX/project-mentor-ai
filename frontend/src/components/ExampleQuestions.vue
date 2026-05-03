<template>
  <div class="welcome-screen">
    <div class="welcome-icon">
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 8V4H8"/>
        <rect width="16" height="12" x="4" y="8" rx="2"/>
        <path d="M2 14h2M20 14h2M15 13v2M9 13v2"/>
      </svg>
    </div>
    <h2>Привет! Я ваш проектный ассистент</h2>
    <p class="welcome-subtitle">
      Задавайте вопросы по управлению проектами, Agile, Scrum, DevOps и другим практикам.
    </p>
    <span class="examples-label">Примеры вопросов:</span>
    <div class="example-grid">
      <button
        v-for="q in questions"
        :key="q"
        class="example-card"
        @click="$emit('select', q)"
      >
        <span>{{ q }}</span>
        <span class="example-arrow">→</span>
      </button>
    </div>
  </div>
</template>

<script setup>
defineEmits(['select'])

const questions = [
  'Как правильно составить ТЗ?',
  'Какие этапы у Scrum?',
  'Как распределить роли в команде?',
  'Что такое Kanban?',
]
</script>

<style scoped>
.welcome-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
  background: rgba(108, 92, 231, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-accent-primary);
  box-shadow: 0 0 40px rgba(108, 92, 231, 0.2);
}

h2 {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text-primary);
  text-align: center;
  margin-bottom: 12px;
}

.welcome-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  text-align: center;
  max-width: 500px;
  margin-bottom: 32px;
}

.examples-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 16px;
}

.example-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  max-width: 600px;
  width: 100%;
}

.example-card {
  background: rgba(18, 20, 56, 0.6);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 14px 18px;
  color: var(--color-text-primary);
  text-align: left;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: var(--font-size-base);
  cursor: pointer;
  transition: all var(--transition-base);
}

.example-card:hover {
  border-color: var(--color-accent-primary);
  background: rgba(108, 92, 231, 0.1);
}

.example-arrow {
  color: var(--color-accent-primary);
  flex-shrink: 0;
  font-size: 16px;
}
</style>
