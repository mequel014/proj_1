// middleware/admin.js
export default defineNuxtRouteMiddleware(async () => {
  const auth = useAuthStore()
  if (!auth.isAuthenticated) return navigateTo('/login')
  if (auth.isAdmin === null) {
    await auth.checkAdmin()
  }
  if (!auth.isAdmin) {
    return navigateTo('/')
  }
})