// middleware/auth.js
export default defineNuxtRouteMiddleware(() => {
  const token = process.client ? localStorage.getItem('auth.token') : null
  if (!token) {
    return navigateTo('/login')
  }
})