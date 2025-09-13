<script setup>
const ch = useCharactersStore()
onMounted(() => ch.fetchPublic())
</script>

<template>
  <div class="container mt-5">
    <h1 class="title is-4">Персонажи</h1>
    <div class="columns is-multiline">
      <div class="column is-3" v-for="c in ch.list" :key="c.id">
        <CharactersCharacterCard :character="c" />
      </div>
    </div>
  </div>
</template>