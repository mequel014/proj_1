<script setup>
definePageMeta({ middleware: ['auth', 'admin'] })
const route = useRoute()
const {$api} = useNuxtApp()
const msgs = ref([])
const err = ref('')

onMounted(async () => {
  try {
    msgs.value = await $api(`/admin/dialogs/${route.params.id}`)
  } catch (e) {
    err.value = 'Ошибка загрузки диалога'
  }
})
</script>

<template>
  <div class="container mt-5">
    <h1 class="title is-4">Диалог #{{ $route.params.id }}</h1>
    <div v-if="err" class="notification is-danger is-light">{{ err }}</div>
    <div class="chat-messages">
      <Chat-MessageBubble v-for="(m, i) in msgs" :key="i" :message="m" />
    </div>
  </div>
</template>