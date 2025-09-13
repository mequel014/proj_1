// plugins/api.js
export default defineNuxtPlugin(() => {
  const apiBase = useRuntimeConfig().public.apiBase

  const setAuth = (options, token) => {
    const hasHeaders = options.headers instanceof Headers
    if (token) {
      if (hasHeaders) options.headers.set('Authorization', `Bearer ${token}`)
      else options.headers = { ...(options.headers || {}), Authorization: `Bearer ${token}` }
    } else {
      if (hasHeaders) options.headers.delete('Authorization')
      else if (options.headers?.Authorization) delete options.headers.Authorization
    }
  }

  const api = $fetch.create({
    baseURL: apiBase,
    headers: { 'Content-Type': 'application/json' },
    onRequest({ options }) {
      options.headers = options.headers instanceof Headers ? options.headers : new Headers(options.headers || {})
      // Лучше брать токен из Pinia, а не из localStorage, чтобы избежать гонок
      const authStore = useAuthStore() // можно получить стор один раз
      const token = authStore.token || (process.client ? localStorage.getItem('auth.token') : '')
      setAuth(options, token)
    },
    onResponseError({ response, request, options }) {
      const status = response?.status
      if (!status) return

      // На 403 не логаутим — это недостаточно прав, не потеря аутентификации
      if (status === 403) return

      // На 401 логаутим только если реально отправляли токен
      const hadAuth = options?.headers instanceof Headers
        ? options.headers.has('Authorization')
        : !!options?.headers?.Authorization

      if (status === 401 && hadAuth && !options?.ignoreAuthErrors) {
        console.warn(`Auth error on ${request}:`, response._data || response.statusText)
        const authStore = useAuthStore() // можно получить стор один раз
        authStore.logout()
      }
    }
  })

  const apiPublic = $fetch.create({
    baseURL: apiBase,
    headers: { 'Content-Type': 'application/json' },
    onRequest({ options }) {
      options.headers = options.headers instanceof Headers ? options.headers : new Headers(options.headers || {})
      if (options.headers instanceof Headers) options.headers.delete('Authorization')
      else if (options.headers?.Authorization) delete options.headers.Authorization
    }
  })

  return { provide: { api, apiPublic } }
})