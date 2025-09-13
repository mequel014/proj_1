<script setup>
definePageMeta({ middleware: 'auth' })
const route = useRoute()
const router = useRouter()
const ch = useCharactersStore()
const id = computed(() => route.params.id)
const character = ref(null)
onMounted(async () => {
  await ch.fetchMine()
  character.value = ch.getById(id.value)
})
async function onSubmit(payload) {
  await ch.updateCharacter(id.value, payload)
  router.push(`/characters/${id.value}`)
}
</script>

<template>
  <div class="container mt-5">
    <div v-if="character">
      <Characters-CharacterForm :model="character" submitText="Сохранить" @submit="onSubmit" />
    </div>
    <div v-else class="notification">Загрузка...</div>
  </div>
</template>