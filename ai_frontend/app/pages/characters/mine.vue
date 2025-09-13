<script setup>
definePageMeta({ middleware: 'auth' })
const ch = useCharactersStore()
onMounted(() => ch.fetchMine())
</script>

<template>
  <div class="container mt-5">
    <h1 class="title is-4">Мои персонажи</h1>
    <div class="columns is-multiline">
      <div class="column is-3" v-for="c in ch.mine" :key="c.id">
        <Characters-CharacterCard :character="c" :mine="true" />
      </div>
    </div>
  </div>
</template>