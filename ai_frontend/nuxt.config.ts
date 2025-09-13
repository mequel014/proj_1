// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  ssr: false,
  devtools: { enabled: false },
  modules: ['@pinia/nuxt'],
  css: [
    '@/assets/css/bulma.min.css',
    '@/assets/css/custom.css',
  ],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    },
  },
})