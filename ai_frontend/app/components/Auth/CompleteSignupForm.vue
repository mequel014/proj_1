<script setup>
const route = useRoute()
const token = ref(route.query.token || '')
const username = ref('')
const password = ref('')
const loading = ref(false)
const err = ref('')
const ok = ref(false)
const auth = useAuthStore()

async function submit() {
  err.value = ''
  loading.value = true
  try {
    await auth.completeSignup({ token: token.value, password: password.value, username: username.value || undefined })
    ok.value = true
  } catch (e) {
    err.value = 'Ошибка завершения регистрации. Проверьте токен.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="box">
    <h1 class="title is-4">Завершение регистрации</h1>
    <div v-if="err" class="notification is-danger is-light">{{ err }}</div>
    <div v-if="ok" class="notification is-primary is-light">
      Готово! Теперь можно <NuxtLink to="/login">войти</NuxtLink>.
    </div>
    <div class="field">
      <label class="label">Token</label>
      <div class="control">
        <input class="input" v-model="token" placeholder="Токен из письма/ссылки" />
      </div>
    </div>
    <div class="field">
      <label class="label">Пароль</label>
      <div class="control">
        <input class="input" type="password" v-model="password" placeholder="••••••••" />
      </div>
    </div>
    <div class="field">
      <label class="label">Username (опционально)</label>
      <div class="control">
        <input class="input" v-model="username" placeholder="nickname" />
      </div>
    </div>
    <div class="field">
      <button class="button is-primary" :class="{ 'is-loading': loading }" @click="submit">Завершить</button>
    </div>
  </div>
</template>