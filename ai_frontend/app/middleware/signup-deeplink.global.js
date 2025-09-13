// middleware/signup-deeplink.global.js
export default defineNuxtRouteMiddleware((to) => {
  // Поддержим разные варианты названий и местоположений токена
  let token = to.query?.token || to.query?.signup_token || to.query?.t

  // Если токен прилетел в hash (например, #token=...), достанем и перекинем
  if (!token && process.client && window.location.hash?.includes('token=')) {
    const params = new URLSearchParams(window.location.hash.replace(/^#/, ''))
    token = params.get('token')
  }

  if (token && to.path !== '/signup/complete') {
    return navigateTo({ path: '/signup/complete', query: { token } })
  }
})