<script setup>
const auth = useAuthStore()
const router = useRouter()
const login = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(login.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = 'Ошибка входа. Проверьте логин/пароль.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="box">
    <h1 class="title is-4">Вход</h1>
    <div v-if="error" class="notification is-danger is-light">{{ error }}</div>
    <div class="field">
      <label class="label">Логин (email или username)</label>
      <div class="control">
        <input class="input" v-model="login" placeholder="email или username" />
      </div>
    </div>
    <div class="field">
      <label class="label">Пароль</label>
      <div class="control">
        <input class="input" type="password" v-model="password" placeholder="••••••••" />
      </div>
    </div>
    <div class="field">
      <button class="button is-primary" :class="{ 'is-loading': loading }" @click="submit">Войти</button>
    </div>
  </div>
</template>