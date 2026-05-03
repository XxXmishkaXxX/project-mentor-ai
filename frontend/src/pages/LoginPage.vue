<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <div class="logo-icon">🛡️</div>
        <h1 class="logo-title">Проектный Ассистент</h1>
        <p class="logo-subtitle">Ваш ИИ-ментор в проектной деятельности</p>
      </div>

      <div class="auth-header">
        <h2>Вход в систему</h2>
        <p>Добро пожаловать! Войдите в свой аккаунт</p>
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="you@example.com"
            :class="{ 'input-error': errors.email }"
          >
          <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label for="password">Пароль</label>
          <div class="password-wrapper">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Введите пароль"
              :class="{ 'input-error': errors.password }"
            >
            <button
              type="button"
              class="toggle-password"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '🙈' : '👁' }}
            </button>
          </div>
          <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
        </div>

        <div v-if="apiError" class="api-error">{{ apiError }}</div>

        <div class="form-extras">
          <label class="checkbox-label">
            <input type="checkbox" v-model="rememberMe">
            <span>Запомнить меня</span>
          </label>
          <span class="forgot-link">Забыли пароль?</span>
        </div>

        <button
          type="submit"
          class="btn-submit"
          :disabled="!isFormValid || authStore.isLoading"
        >
          <span v-if="authStore.isLoading" class="spinner" />
          <span v-else>Войти</span>
        </button>

        <p class="auth-switch">
          Нет аккаунта?
          <router-link to="/register">Зарегистрироваться</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })
const apiError = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const isFormValid = computed(() =>
  form.email && form.password && emailRegex.test(form.email)
)

function validate() {
  errors.email = ''
  errors.password = ''
  let valid = true

  if (!form.email) {
    errors.email = 'Введите email'
    valid = false
  } else if (!emailRegex.test(form.email)) {
    errors.email = 'Некорректный формат email'
    valid = false
  }

  if (!form.password) {
    errors.password = 'Введите пароль'
    valid = false
  }

  return valid
}

async function handleSubmit() {
  apiError.value = ''
  if (!validate()) return

  try {
    await authStore.login(form.email, form.password)
    router.push('/chat')
  } catch (err) {
    if (err.status === 401) {
      apiError.value = 'Неверный email или пароль'
    } else if (err.status === 422 && err.data?.extra) {
      for (const e of err.data.extra) {
        if (e.key === 'email') errors.email = e.message
        if (e.key === 'password') errors.password = e.message
      }
    } else {
      apiError.value = 'Ошибка сети. Проверьте подключение'
    }
  }
}
</script>

<style scoped>
.auth-page {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
}

.auth-card {
  width: 420px;
  max-width: 90vw;
  background: rgba(13, 16, 51, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 40px;
  box-shadow: var(--shadow-card);
  animation: fadeInUp var(--transition-slow) ease;
}

.auth-logo {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  font-size: 40px;
  margin-bottom: 8px;
}

.logo-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.logo-subtitle {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.auth-header {
  margin-bottom: 24px;
}

.auth-header h2 {
  font-size: var(--font-size-lg);
  margin-bottom: 4px;
}

.auth-header p {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
}

.form-group {
  margin-bottom: 16px;
}

.password-wrapper {
  position: relative;
}

.password-wrapper input {
  padding-right: 44px;
}

.toggle-password {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
}

.input-error {
  border-color: var(--color-accent-red) !important;
}

.field-error {
  color: var(--color-accent-red);
  font-size: 13px;
  margin-top: 4px;
  display: block;
}

.api-error {
  color: var(--color-accent-red);
  font-size: 13px;
  text-align: center;
  margin-bottom: 12px;
  animation: fadeInUp var(--transition-slow) ease;
}

.form-extras {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  margin-bottom: 0;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  height: auto;
}

.forgot-link {
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: default;
}

.btn-submit {
  width: 100%;
  height: 48px;
  background: var(--color-accent-green);
  color: #fff;
  font-weight: 600;
  font-size: var(--font-size-base);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.btn-submit:hover:not(:disabled) {
  filter: brightness(1.1);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-switch {
  text-align: center;
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.auth-switch a {
  color: var(--color-accent-primary);
  font-weight: 500;
}
</style>
