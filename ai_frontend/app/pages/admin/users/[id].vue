<script setup>
definePageMeta({ middleware: ['auth', 'admin'] })
const route = useRoute()
const {$api} = useNuxtApp()
const info = ref(null)
const err = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  err.value = ''
  try {
    info.value = await $api(`/admin/users/${route.params.id}`)
  } catch (e) {
    err.value = 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}
onMounted(load)

async function blockCharacter(id) {
  if (!confirm('Заблокировать персонажа?')) return
  await $api(`/characters/${id}/block`, { method: 'POST' })
  await load()
}
</script>

<template>
  <div class="container mt-5">
    <h1 class="title is-4">Пользователь #{{ $route.params.id }}</h1>
    <div v-if="err" class="notification is-danger is-light">{{ err }}</div>
    <div v-if="loading">Загрузка...</div>

    <div v-if="info" class="content">
      <p>Дата регистрации: <strong>{{ new Date(info.registered_at || info.created_at || Date.now()).toLocaleString() }}</strong></p>

      <h2 class="title is-5 mt-5">Созданные персонажи</h2>
      <div class="columns is-multiline">
        <div class="column is-4" v-for="c in (info.characters || [])" :key="c.id">
          <div class="card">
            <div class="card-content">
              <p class="title is-6">{{ c.name }}</p>
              <!-- <div class="tags">
                <span class="tag" v-for="t in (c.interests || [])" :key="t">{{ t }}</span>
              </div> -->
              <div class="buttons">
                <NuxtLink :to="`/characters/${c.id}`" class="button is-small is-link">Открыть</NuxtLink>
                <button class="button is-small is-danger" @click="blockCharacter(c.id)">Блокировать</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <h2 class="title is-5 mt-5">Диалоги (короткий список)</h2>
      <div class="box" v-for="d in (info.short_dialogs || [])" :key="d.id">
        <div class="level">
          <div class="level-left">
            <div>
              <div class="has-text-weight-semibold">{{ d.character_name }}</div>
              <div class="is-size-7 has-text-grey">{{ new Date(d.started_at).toLocaleString() }}</div>
            </div>
          </div>
          <div class="level-right">
            <NuxtLink :to="`/admin/dialogs/${d.id}`" class="button is-small is-primary">Открыть</NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>