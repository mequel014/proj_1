// stores/auth.js
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(process.client ? localStorage.getItem('auth.token') : '')
  const isAdmin = ref(null) // null = неизвестно, true/false после проверки
  const loginName = ref(process.client ? localStorage.getItem('auth.loginName') : '')

  const isAuthenticated = computed(() => !!token.value)

  watch(token, (v) => {
    if (!process.client) return
    if (v) localStorage.setItem('auth.token', v)
    else localStorage.removeItem('auth.token')
  })
  watch(loginName, (v) => {
    if (!process.client) return
    if (v) localStorage.setItem('auth.loginName', v)
    else localStorage.removeItem('auth.loginName')
  })

  const {$api} = useNuxtApp()

  async function requestSignup(email) {
    await $api('/auth/request-signup', { method: 'POST', body: { email } })
  }

  async function completeSignup(payload) {
    // payload: { token, password, username? }
    await $api('/auth/complete-signup', { method: 'POST', body: payload })
  }

  async function login(login, password) {
    const res = await $api('/auth/login', { method: 'POST', body: { login, password } })
    token.value = res?.access_token || ''
    loginName.value = login
    await checkAdmin()
  }

  async function checkAdmin() {
    if (!token.value) { isAdmin.value = false; return }
    try {
      await $api('/admin/stats', { method: 'GET' })
      isAdmin.value = true
    } catch (e) {
      isAdmin.value = false
    }
  }

  function logout() {
    token.value = ''
    loginName.value = ''
    isAdmin.value = null
    navigateTo('/login')
  }

  return { token, isAdmin, loginName, isAuthenticated, requestSignup, completeSignup, login, checkAdmin, logout }
})