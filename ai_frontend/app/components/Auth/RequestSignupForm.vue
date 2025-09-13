<script setup>
const auth = useAuthStore()
const email = ref('')
const sent = ref(false)
const err = ref('')
const loading = ref(false)

async function submit() {
  err.value = ''
  loading.value = true
  try {
    await auth.requestSignup(email.value)
    sent.value = true
  } catch (e) {
    err.value = 'Не удалось отправить письмо.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="box">
    <h1 class="title is-4">Регистрация по email</h1>
    <p class="subtitle is-6">Мы отправим ссылку на указанный адрес.</p>
    <div v-if="err" class="notification is-danger is-light">{{ err }}</div>
    <div v-if="sent" class="notification is-primary is-light">
      Ссылка отправлена. Проверьте почту (в dev-режиме — ссылку смотрите в логах сервера).
    </div>
    <div class="field">
      <label class="label">Email</label>
      <div class="control">
        <input class="input" v-model="email" placeholder="you@domain.com" type="email" />
      </div>
    </div>
    <div class="field">
      <button class="button is-primary" :class="{ 'is-loading': loading }" @click="submit">Отправить</button>
    </div>
  </div>
</template>