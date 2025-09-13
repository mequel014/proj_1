<script setup>
definePageMeta({ middleware: ['auth', 'admin'] })
const {$api} = useNuxtApp()
const users = ref([])
const loading = ref(false)
const err = ref('')

async function load() {
  loading.value = true
  err.value = ''
  try {
    users.value = await $api('/admin/users')
  } catch (e) {
    err.value = 'Ошибка загрузки пользователей'
  } finally {
    loading.value = false
  }
}
onMounted(load)

async function blockUser(u) {
  if (!confirm(`Заблокировать пользователя ${u.username || u.email}?`)) return
  await $api(`/admin/users/${u.id}/block`, { method: 'POST' })
  await load()
}
</script>

<template>
  <div class="container mt-5">
    <h1 class="title is-4">Пользователи</h1>
    <div v-if="err" class="notification is-danger is-light">{{ err }}</div>
    <div class="box" v-for="u in users" :key="u.id">
      <div class="level">
        <div class="level-left">
          <div>
            <div class="has-text-weight-semibold">{{ u.username || u.email }}</div>
            <div class="is-size-7 has-text-grey">ID: {{ u.id }}</div>
          </div>
        </div>
        <div class="level-right">
          <NuxtLink :to="`/admin/users/${u.id}`" class="button is-small is-link">Открыть</NuxtLink>
          <button class="button is-small is-danger ml-2" @click="blockUser(u)">Блокировать</button>
        </div>
      </div>
    </div>
  </div>
</template>