<script setup>
definePageMeta({ middleware: 'auth' })
const ch = useCharactersStore()
const router = useRouter()
async function onSubmit(payload) {
  const created = await ch.createCharacter(payload)
  router.push(`/characters/${created.id}`)
}
</script>

<template>
  <div class="container mt-5">
    <Characters-CharacterForm :model="{}" submitText="Создать" @submit="onSubmit" />
  </div>
</template>