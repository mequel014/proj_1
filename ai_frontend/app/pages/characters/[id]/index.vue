<script setup>
const route = useRoute()
const ch = useCharactersStore()
const id = computed(() => route.params.id)
const character = computed(() => ch.getById(id.value))
onMounted(async () => {
  if (!character.value) {
    await ch.fetchPublic()
    await ch.fetchMine()
  }
})
</script>

<template>
  <div class="container mt-5">
    <div v-if="character">
      <h1 class="title is-4">Чат: {{ character.name }}</h1>
      <ChatWindow :character="character" />
    </div>
    <div v-else class="notification">Загрузка персонажа...</div>
  </div>
</template>