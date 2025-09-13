<script setup>
definePageMeta({ middleware: ['auth', 'admin'] })
const {$api} = useNuxtApp()
const stats = ref(null)
const err = ref('')
onMounted(async () => {
  try {
    stats.value = await $api('/admin/stats')
  } catch (e) {
    err.value = 'Не удалось получить статистику'
  }
})
</script>

<template>
  <div class="container mt-5">
    <h1 class="title is-4">Админка — Статистика</h1>
    <div v-if="err" class="notification is-danger is-light">{{ err }}</div>
    <div class="columns" v-if="stats">
      <div class="column">
        <div class="box">
          <p class="title is-5">Пользователи</p>
          <p class="is-size-3">{{ stats.users ?? '—' }}</p>
        </div>
      </div>
      <div class="column">
        <div class="box">
          <p class="title is-5">Диалоги</p>
          <p class="is-size-3">{{ stats.dialogs ?? '—' }}</p>
        </div>
      </div>
      <div class="column">
        <div class="box">
          <p class="title is-5">Персонажи</p>
          <p class="is-size-3">{{ stats.characters ?? '—' }}</p>
        </div>
      </div>
    </div>
    <NuxtLink to="/admin/users" class="button is-primary mt-3">Пользователи</NuxtLink>
  </div>
</template>