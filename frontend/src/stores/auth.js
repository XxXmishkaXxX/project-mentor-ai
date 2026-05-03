import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '../api/auth.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(email, password) {
    isLoading.value = true
    try {
      user.value = await authApi.login(email, password)
    } finally {
      isLoading.value = false
    }
  }

  async function register(username, email, password) {
    isLoading.value = true
    try {
      await authApi.register(username, email, password)
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    await authApi.logout()
    user.value = null
  }

  async function fetchMe() {
    try {
      user.value = await authApi.getMe()
    } catch {
      user.value = null
    }
  }

  return {
    user,
    isLoading,
    isAuthenticated,
    isAdmin,
    login,
    register,
    logout,
    fetchMe,
  }
})
