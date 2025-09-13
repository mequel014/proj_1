<script setup>
definePageMeta({ middleware: 'auth' })
const profile = useProfileStore()
</script>

<template>
  <div class="container mt-5">
    <div class="box">
      <h1 class="title is-4">Мой профиль</h1>
      <div class="field">
        <label class="label">Bio</label>
        <textarea class="textarea" v-model="profile.bio" rows="2" placeholder="Коротко о себе"></textarea>
      </div>
      <div class="field">
        <label class="label">Описание</label>
        <textarea class="textarea" v-model="profile.description" rows="5" placeholder="Подробнее о себе"></textarea>
      </div>
      <p class="help">Временное локальное хранение до появления backend-эндпоинта.</p>
    </div>
  </div>
</template>