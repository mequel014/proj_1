// stores/profile.js
import { defineStore } from 'pinia'

export const useProfileStore = defineStore('profile', () => {
  const bio = ref(process.client ? localStorage.getItem('profile.bio') || '' : '')
  const description = ref(process.client ? localStorage.getItem('profile.description') || '' : '')

  watch(bio, (v) => { if (process.client) localStorage.setItem('profile.bio', v) })
  watch(description, (v) => { if (process.client) localStorage.setItem('profile.description', v) })

  return { bio, description }
})