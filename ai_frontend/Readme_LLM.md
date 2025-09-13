Ниже — готовый каркас фронтенда на Nuxt 3 + Pinia (Composition API, .js), стили Bulma + custom.css, разложенный по компонентам/страницам/плагинам. Покрывает ваш API: регистрация по email-ссылке, логин (JWT), список/карточки персонажей, чат-окна, создание/редакт персонажей, список диалогов, а также Админку (статистика, пользователи, диалоги, блокировки).

Важно:
- Профиль пользователя (bio/description) — временно храню локально (localStorage) из‑за отсутствия эндпоинта в API.
- Для запросов к API используем плагин $api (обёртка над $fetch), токен подставляется автоматически.
- Стили: Bulma + немного custom.css; в компонентах — style scoped.

Структура проекта
- assets/css/bulma.min.css  ← положите сюда bulma
- assets/css/custom.css
- components/
  - AppNavbar.vue
  - Auth/LoginForm.vue
  - Auth/RequestSignupForm.vue
  - Auth/CompleteSignupForm.vue
  - Chat/ChatWindow.vue
  - Chat/MessageBubble.vue
  - Characters/CharacterCard.vue
  - Characters/CharacterForm.vue
  - UI/TagInput.vue
- middleware/
  - auth.js
  - admin.js
- pages/
  - index.vue
  - login.vue
  - signup/index.vue
  - signup/complete.vue
  - characters/index.vue
  - characters/mine.vue
  - characters/new.vue
  - characters/[id].vue         ← чат со стартом диалога
  - characters/[id]/edit.vue
  - dialogs/index.vue
  - dialogs/[id].vue            ← чат по dialog_id
  - admin/index.vue
  - admin/users/index.vue
  - admin/users/[id].vue
  - admin/dialogs/[id].vue
- plugins/
  - api.client.js
- stores/
  - auth.js
  - characters.js
  - dialogs.js
  - profile.js
- nuxt.config.js
- .env (пример)
  - NUXT_PUBLIC_API_BASE=http://localhost:8000

nuxt.config.js
```js
// nuxt.config.js
export default defineNuxtConfig({
  modules: ['@pinia/nuxt'],
  css: [
    '@/assets/css/bulma.min.css',
    '@/assets/css/custom.css',
  ],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    },
  },
})
```

assets/css/custom.css
```css
/* assets/css/custom.css */
:root {
  --bg: #0f1220;
  --card: #1a1f36;
  --text: #f3f3f4;
  --muted: #aab0c6;
  --primary: #5b8def;
  --tag: #2d3350;
}
html, body {
  background: var(--bg);
  color: var(--text);
}
a, .button.is-link, .is-primary {
  background-color: var(--primary) !important;
  border-color: var(--primary) !important;
}
.card {
  background: var(--card);
  color: var(--text);
}
.tag {
  background: var(--tag);
  color: var(--text);
}
.input, .textarea, .select select {
  background: #14182b;
  border-color: #2b3050;
  color: var(--text);
}
.notification {
  background: #1c2342;
  color: var(--text);
  border: 1px solid #2b3050;
}
.chat-container {
  display: flex; flex-direction: column; height: calc(100vh - 160px);
}
.chat-messages {
  flex: 1; overflow-y: auto; padding: 1rem; gap: 0.5rem; display: flex; flex-direction: column;
}
.chat-input {
  border-top: 1px solid #2b3050; padding: 0.75rem; background: #151a31;
}
.bubble {
  padding: 0.75rem 1rem; border-radius: 10px; max-width: 80%;
}
.bubble.user { align-self: flex-end; background: #2b3050; }
.bubble.assistant { align-self: flex-start; background: #242a49; }
.bubble.system { align-self: center; background: #1b213f; font-style: italic; }
```

plugins/api.client.js
```js
// plugins/api.client.js
export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()
  const api = $fetch.create({
    baseURL: config.public.apiBase,
    credentials: 'omit',
    headers: { 'Content-Type': 'application/json' },
    onRequest({ options }) {
      const token = localStorage.getItem('auth.token')
      options.headers = options.headers || {}
      if (token) {
        options.headers.Authorization = `Bearer ${token}`
      }
    },
  })
  return { provide: { api } }
})
```

middleware/auth.js
```js
// middleware/auth.js
export default defineNuxtRouteMiddleware(() => {
  const token = process.client ? localStorage.getItem('auth.token') : null
  if (!token) {
    return navigateTo('/login')
  }
})
```

middleware/admin.js
```js
// middleware/admin.js
export default defineNuxtRouteMiddleware(async () => {
  const auth = useAuthStore()
  if (!auth.isAuthenticated) return navigateTo('/login')
  if (auth.isAdmin === null) {
    await auth.checkAdmin()
  }
  if (!auth.isAdmin) {
    return navigateTo('/')
  }
})
```

stores/auth.js
```js
// stores/auth.js
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(process.client ? localStorage.getItem('auth.token') : '')
  const isAdmin = ref(null) // null = неизвестно, true/false после проверки
  const loginName = ref(process.client ? localStorage.getItem('auth.loginName') : '')

  const isAuthenticated = computed(() => !!token.value)

  watch(token, (v) => {
    if (!process.client) return
    if (v) localStorage.setItem('auth.token', v)
    else localStorage.removeItem('auth.token')
  })
  watch(loginName, (v) => {
    if (!process.client) return
    if (v) localStorage.setItem('auth.loginName', v)
    else localStorage.removeItem('auth.loginName')
  })

  const {$api} = useNuxtApp()

  async function requestSignup(email) {
    await $api('/auth/request-signup', { method: 'POST', body: { email } })
  }

  async function completeSignup(payload) {
    // payload: { token, password, username? }
    await $api('/auth/complete-signup', { method: 'POST', body: payload })
  }

  async function login(login, password) {
    const res = await $api('/auth/login', { method: 'POST', body: { login, password } })
    token.value = res?.access_token || ''
    loginName.value = login
    await checkAdmin()
  }

  async function checkAdmin() {
    if (!token.value) { isAdmin.value = false; return }
    try {
      await $api('/admin/stats', { method: 'GET' })
      isAdmin.value = true
    } catch (e) {
      isAdmin.value = false
    }
  }

  function logout() {
    token.value = ''
    loginName.value = ''
    isAdmin.value = null
    navigateTo('/login')
  }

  return { token, isAdmin, loginName, isAuthenticated, requestSignup, completeSignup, login, checkAdmin, logout }
})
```

stores/profile.js (локально храним bio/description)
```js
// stores/profile.js
import { defineStore } from 'pinia'

export const useProfileStore = defineStore('profile', () => {
  const bio = ref(process.client ? localStorage.getItem('profile.bio') || '' : '')
  const description = ref(process.client ? localStorage.getItem('profile.description') || '' : '')

  watch(bio, (v) => { if (process.client) localStorage.setItem('profile.bio', v) })
  watch(description, (v) => { if (process.client) localStorage.setItem('profile.description', v) })

  return { bio, description }
})
```

stores/characters.js
```js
// stores/characters.js
import { defineStore } from 'pinia'

export const useCharactersStore = defineStore('characters', () => {
  const list = ref([])      // публичные
  const mine = ref([])      // мои
  const loading = ref(false)
  const {$api} = useNuxtApp()

  async function fetchPublic() {
    loading.value = true
    try {
      list.value = await $api('/characters')
    } finally {
      loading.value = false
    }
  }
  async function fetchMine() {
    loading.value = true
    try {
      mine.value = await $api('/characters?mine=true')
    } finally {
      loading.value = false
    }
  }
  async function createCharacter(payload) {
    // ожидаемые поля: { name, gender, interests: string[], context, is_public: boolean, photo_url, rating? }
    return await $api('/characters', { method: 'POST', body: payload })
  }
  async function updateCharacter(id, payload) {
    return await $api(`/characters/${id}`, { method: 'PATCH', body: payload })
  }
  async function uploadPhoto(file) {
    const form = new FormData()
    form.append('file', file)
    // принудительно меняем заголовки под multipart
    return await $fetch(`${useRuntimeConfig().public.apiBase}/characters/upload/photo`, {
      method: 'POST', body: form,
      headers: { Authorization: `Bearer ${localStorage.getItem('auth.token') || ''}` },
    })
  }

  function getById(id) {
    return mine.value.find(c => c.id == id) || list.value.find(c => c.id == id)
  }

  return { list, mine, loading, fetchPublic, fetchMine, createCharacter, updateCharacter, uploadPhoto, getById }
})
```

stores/dialogs.js
```js
// stores/dialogs.js
import { defineStore } from 'pinia'

export const useDialogsStore = defineStore('dialogs', () => {
  const dialogs = ref([]) // список моих диалогов
  const messages = ref({}) // { [dialogId]: Message[] }
  const {$api} = useNuxtApp()

  async function fetchDialogs() {
    dialogs.value = await $api('/dialogs')
  }

  async function fetchMessages(dialogId) {
    const res = await $api(`/dialogs/${dialogId}/messages`)
    messages.value[dialogId] = res
    return res
  }

  async function sendMessage({ characterId, text, dialogId = null }) {
    const body = { text }
    if (dialogId) body.dialog_id = dialogId
    const res = await $api(`/dialogs/${characterId}/messages`, { method: 'POST', body })
    // Ожидаем res = { dialog_id, message?, assistant? } — подстрахуемся:
    const newDialogId = res.dialog_id || dialogId
    if (!messages.value[newDialogId]) messages.value[newDialogId] = []
    // добавим юзерское
    messages.value[newDialogId].push({ role: 'user', text, created_at: new Date().toISOString() })
    // добавим ответ ассистента
    const assistantMsg = res.message || res.assistant || res.reply || null
    if (assistantMsg) {
      messages.value[newDialogId].push(
        typeof assistantMsg === 'string'
          ? { role: 'assistant', text: assistantMsg }
          : assistantMsg
      )
    }
    // если новый диалог — освежим список
    if (!dialogId) await fetchDialogs()
    return newDialogId
  }

  return { dialogs, messages, fetchDialogs, fetchMessages, sendMessage }
})
```

components/AppNavbar.vue
```vue
<script setup>
const auth = useAuthStore()
const router = useRouter()

const goHome = () => router.push('/')
</script>

<template>
  <nav class="navbar is-dark" role="navigation" aria-label="main navigation">
    <div class="navbar-brand">
      <a class="navbar-item" @click.prevent="goHome">🗨️ PersonaTalk</a>
      <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false" data-target="navMenu">
        <span aria-hidden="true"></span><span aria-hidden="true"></span><span aria-hidden="true"></span>
      </a>
    </div>

    <div id="navMenu" class="navbar-menu">
      <div class="navbar-start">
        <NuxtLink to="/characters" class="navbar-item">Персонажи</NuxtLink>
        <NuxtLink to="/dialogs" class="navbar-item" v-if="auth.isAuthenticated">Диалоги</NuxtLink>
        <NuxtLink to="/characters/mine" class="navbar-item" v-if="auth.isAuthenticated">Мои персонажи</NuxtLink>
        <NuxtLink to="/characters/new" class="navbar-item" v-if="auth.isAuthenticated">Создать</NuxtLink>
        <NuxtLink to="/admin" class="navbar-item" v-if="auth.isAdmin">Админка</NuxtLink>
      </div>
      <div class="navbar-end">
        <div class="navbar-item">
          <div class="buttons" v-if="!auth.isAuthenticated">
            <NuxtLink to="/signup" class="button is-primary">Регистрация</NuxtLink>
            <NuxtLink to="/login" class="button is-light">Войти</NuxtLink>
          </div>
          <div class="buttons" v-else>
            <NuxtLink to="/profile" class="button is-info is-light" title="Профиль">{{ auth.loginName || 'Профиль' }}</NuxtLink>
            <button class="button is-light" @click="auth.logout()">Выйти</button>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar { background: #14182b; border-bottom: 1px solid #2b3050; }
</style>
```

components/Auth/LoginForm.vue
```vue
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
```

components/Auth/RequestSignupForm.vue
```vue
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
```

components/Auth/CompleteSignupForm.vue
```vue
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
```

components/UI/TagInput.vue
```vue
<script setup>
const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'интересы (через Enter)' }
})
const emit = defineEmits(['update:modelValue'])

const input = ref('')
function addTag() {
  const v = input.value.trim()
  if (!v) return
  const tags = Array.from(new Set([...(props.modelValue || []), v]))
  emit('update:modelValue', tags)
  input.value = ''
}
function removeTag(tag) {
  emit('update:modelValue', (props.modelValue || []).filter(t => t !== tag))
}
function onKey(e) {
  if (e.key === 'Enter') addTag()
}
</script>

<template>
  <div>
    <div class="tags">
      <span class="tag" v-for="tag in modelValue" :key="tag">
        {{ tag }}
        <button class="delete is-small" @click="removeTag(tag)"></button>
      </span>
    </div>
    <input class="input" v-model="input" :placeholder="placeholder" @keydown="onKey" />
    <p class="help">Нажмите Enter для добавления тега</p>
  </div>
</template>

<style scoped>
.tags { margin-bottom: 0.5rem; flex-wrap: wrap; }
.tag { margin: 0.2rem; }
</style>
```

components/Characters/CharacterCard.vue
```vue
<script setup>
const props = defineProps({ character: { type: Object, required: true }, mine: { type: Boolean, default: false } })
const router = useRouter()
function openChat() {
  router.push(`/characters/${props.character.id}`)
}
function edit() {
  router.push(`/characters/${props.character.id}/edit`)
}
</script>

<template>
  <div class="card">
    <div class="card-content">
      <div class="media">
        <div class="media-left" v-if="character.photo_url">
          <figure class="image is-64x64">
            <img :src="character.photo_url" :alt="character.name" style="object-fit: cover;">
          </figure>
        </div>
        <div class="media-content">
          <p class="title is-5">{{ character.name }}</p>
          <p class="subtitle is-6">
            <span class="tag is-dark">{{ character.gender || '—' }}</span>
            <span class="tag is-link ml-2">⭐ {{ character.rating ?? '—' }}</span>
            <span class="tag is-warning ml-2" v-if="character.is_public === false">private</span>
          </p>
        </div>
      </div>
      <div class="content">
        <div class="tags">
          <span class="tag" v-for="tag in character.interests || []" :key="tag">{{ tag }}</span>
        </div>
      </div>
      <div class="buttons">
        <button class="button is-primary" @click="openChat">Чат</button>
        <button class="button" v-if="mine" @click="edit">Редактировать</button>
      </div>
    </div>
  </div>
</template>
```

components/Characters/CharacterForm.vue
```vue
<script setup>
const props = defineProps({
  model: { type: Object, default: () => ({}) },
  submitText: { type: String, default: 'Создать' }
})
const emit = defineEmits(['submit'])

const name = ref(props.model.name || '')
const gender = ref(props.model.gender || '')
const interests = ref(props.model.interests || [])
const context = ref(props.model.context || '')
const is_public = ref(props.model.is_public ?? true)
const photo_url = ref(props.model.photo_url || '')
const rating = ref(props.model.rating || '')

const loading = ref(false)
const error = ref('')
const chStore = useCharactersStore()

async function handlePhoto(e) {
  const file = e.target.files?.[0]
  if (!file) return
  try {
    const res = await chStore.uploadPhoto(file)
    photo_url.value = res.photo_url || res.url || ''
  } catch (e) {
    error.value = 'Ошибка загрузки фото'
  }
}

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    const payload = {
      name: name.value,
      gender: gender.value,
      interests: interests.value,
      context: context.value,
      is_public: is_public.value,
      photo_url: photo_url.value,
      rating: rating.value ? Number(rating.value) : undefined
    }
    await emit('submit', payload)
  } catch (e) {
    error.value = 'Ошибка сохранения персонажа'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="box">
    <h2 class="title is-5">{{ submitText === 'Создать' ? 'Новый персонаж' : 'Редактирование персонажа' }}</h2>
    <div v-if="error" class="notification is-danger is-light">{{ error }}</div>
    <div class="columns">
      <div class="column is-8">
        <div class="field">
          <label class="label">Имя</label>
          <input class="input" v-model="name" placeholder="Имя персонажа" />
        </div>
        <div class="field">
          <label class="label">Пол</label>
          <div class="select is-fullwidth">
            <select v-model="gender">
              <option value="">—</option>
              <option>male</option>
              <option>female</option>
              <option>other</option>
            </select>
          </div>
        </div>
        <div class="field">
          <label class="label">Интересы</label>
          <UI-TagInput v-model="interests" placeholder="Добавьте интересы (Enter)"/>
        </div>
        <div class="field">
          <label class="label">Контекст (системное сообщение)</label>
          <textarea class="textarea" v-model="context" rows="5" placeholder="Обстановка, мысли, стиль ответа и т.д."></textarea>
        </div>
        <div class="field">
          <label class="label">Рейтинг (например 7.7)</label>
          <input class="input" v-model="rating" placeholder="7.7" />
        </div>
        <div class="field">
          <label class="checkbox">
            <input type="checkbox" v-model="is_public" /> public (виден всем)
          </label>
        </div>
        <div class="field">
          <button class="button is-primary" :class="{ 'is-loading': loading }" @click="handleSubmit">{{ submitText }}</button>
        </div>
      </div>
      <div class="column is-4">
        <div class="field">
          <label class="label">Фото</label>
          <div class="file has-name is-fullwidth">
            <label class="file-label">
              <input class="file-input" type="file" accept="image/*" @change="handlePhoto" />
              <span class="file-cta">
                <span class="file-label">Выберите файл…</span>
              </span>
              <span class="file-name" v-if="photo_url">{{ photo_url }}</span>
            </label>
          </div>
          <figure class="image is-1by1" v-if="photo_url" style="margin-top: 0.5rem;">
            <img :src="photo_url" alt="Фото персонажа" style="object-fit: cover;">
          </figure>
        </div>
      </div>
    </div>
  </div>
</template>
```

components/Chat/MessageBubble.vue
```vue
<script setup>
const props = defineProps({ message: { type: Object, required: true } })
const role = computed(() => props.message.role || 'assistant')
</script>

<template>
  <div class="bubble" :class="role">
    <div v-if="role === 'system'"><em>{{ message.text || message.content }}</em></div>
    <div v-else>{{ message.text || message.content }}</div>
  </div>
</template>

<style scoped>
.bubble { margin: 0.25rem 0; }
</style>
```

components/Chat/ChatWindow.vue
```vue
<script setup>
const props = defineProps({
  character: { type: Object, default: null },
  dialogId: { type: [String, Number], default: null }
})

const dialogs = useDialogsStore()
const route = useRoute()
const router = useRouter()
const messages = computed(() => dialogs.messages[currentDialogId.value] || [])
const input = ref('')
const sending = ref(false)
const currentDialogId = ref(props.dialogId || null)

// При заходе с dialogId — подтянуть историю
onMounted(async () => {
  if (currentDialogId.value) {
    await dialogs.fetchMessages(currentDialogId.value)
  }
})

// Отправка сообщения: если диалог не создан — создастся на сервере
async function send() {
  const text = input.value.trim()
  if (!text) return
  sending.value = true
  try {
    const newId = await dialogs.sendMessage({
      characterId: props.character?.id || route.params.id,
      text,
      dialogId: currentDialogId.value || null
    })
    input.value = ''
    // если новый диалог — зафиксируем id и обновим роут, если мы на /characters/:id
    if (!currentDialogId.value) {
      currentDialogId.value = newId
      if (route.name?.toString().includes('characters-id')) {
        router.push(`/dialogs/${newId}`)
      }
    }
    // если истории не было — подтянуть на всякий случай
    if (!messages.value.length) {
      await dialogs.fetchMessages(newId)
    }
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <div class="chat-container">
    <div class="chat-messages">
      <!-- Покажем контекст до первого сообщения, если диалог только создаётся -->
      <Chat-MessageBubble v-if="!currentDialogId && character?.context" :message="{ role: 'system', text: character.context }" />
      <Chat-MessageBubble v-for="(m, i) in messages" :key="i" :message="m" />
    </div>
    <div class="chat-input">
      <div class="field has-addons">
        <div class="control is-expanded">
          <input class="input" v-model="input" placeholder="Введите сообщение" @keydown.enter.prevent="send" />
        </div>
        <div class="control">
          <button class="button is-primary" :class="{ 'is-loading': sending }" @click="send">Отправить</button>
        </div>
      </div>
    </div>
  </div>
</template>
```

pages/index.vue (публичные карточки)
```vue
<script setup>
definePageMeta({ layout: 'default' })
const ch = useCharactersStore()
onMounted(() => ch.fetchPublic())
</script>

<template>
  <div class="container mt-5">
    <AppNavbar />
    <h1 class="title is-4">Публичные персонажи</h1>
    <div class="columns is-multiline">
      <div class="column is-3" v-for="c in ch.list" :key="c.id">
        <Characters-CharacterCard :character="c" />
      </div>
    </div>
  </div>
</template>
```

pages/login.vue
```vue
<script setup>
</script>

<template>
  <div class="container mt-5">
    <AppNavbar />
    <div class="columns is-centered">
      <div class="column is-5">
        <Auth-LoginForm />
      </div>
    </div>
  </div>
</template>
```

pages/signup/index.vue
```vue
<script setup>
</script>

<template>
  <div class="container mt-5">
    <AppNavbar />
    <div class="columns is-centered">
      <div class="column is-6">
        <Auth-RequestSignupForm />
      </div>
    </div>
  </div>
</template>
```

pages/signup/complete.vue
```vue
<script setup>
</script>

<template>
  <div class="container mt-5">
    <AppNavbar />
    <div class="columns is-centered">
      <div class="column is-6">
        <Auth-CompleteSignupForm />
      </div>
    </div>
  </div>
</template>
```

pages/characters/index.vue
```vue
<script setup>
const ch = useCharactersStore()
onMounted(() => ch.fetchPublic())
</script>

<template>
  <div class="container mt-5">
    <AppNavbar />
    <h1 class="title is-4">Персонажи</h1>
    <div class="columns is-multiline">
      <div class="column is-3" v-for="c in ch.list" :key="c.id">
        <Characters-CharacterCard :character="c" />
      </div>
    </div>
  </div>
</template>
```

pages/characters/mine.vue
```vue
<script setup>
definePageMeta({ middleware: 'auth' })
const ch = useCharactersStore()
onMounted(() => ch.fetchMine())
</script>

<template>
  <div class="container mt-5">
    <AppNavbar />
    <h1 class="title is-4">Мои персонажи</h1>
    <div class="columns is-multiline">
      <div class="column is-3" v-for="c in ch.mine" :key="c.id">
        <Characters-CharacterCard :character="c" :mine="true" />
      </div>
    </div>
  </div>
</template>
```

pages/characters/new.vue
```vue
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
    <AppNavbar />
    <Characters-CharacterForm :model="{}" submitText="Создать" @submit="onSubmit" />
  </div>
</template>
```

pages/characters/[id].vue (окно чата c первым сообщением — создаст диалог)
```vue
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
    <AppNavbar />
    <div v-if="character">
      <h1 class="title is-4">Чат: {{ character.name }}</h1>
      <Chat-ChatWindow :character="character" />
    </div>
    <div v-else class="notification">Загрузка персонажа...</div>
  </div>
</template>
```

pages/characters/[id]/edit.vue
```vue
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
    <AppNavbar />
    <div v-if="character">
      <Characters-CharacterForm :model="character" submitText="Сохранить" @submit="onSubmit" />
    </div>
    <div v-else class="notification">Загрузка...</div>
  </div>
</template>
```

pages/dialogs/index.vue
```vue
<script setup>
definePageMeta({ middleware: 'auth' })
const d = useDialogsStore()
onMounted(() => d.fetchDialogs())
</script>

<template>
  <div class="container mt-5">
    <AppNavbar />
    <h1 class="title is-4">Мои диалоги</h1>
    <div class="box" v-for="dlg in d.dialogs" :key="dlg.id">
      <div class="level">
        <div class="level-left">
          <div>
            <div class="has-text-weight-semibold">{{ dlg.character_name || dlg.character?.name || 'Персонаж' }}</div>
            <div class="is-size-7 has-text-grey">{{ new Date(dlg.created_at || dlg.updated_at || Date.now()).toLocaleString() }}</div>
          </div>
        </div>
        <div class="level-right">
          <NuxtLink class="button is-small is-primary" :to="`/dialogs/${dlg.id}`">Открыть</NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>
```

pages/dialogs/[id].vue
```vue
<script setup>
definePageMeta({ middleware: 'auth' })
const route = useRoute()
const dialogs = useDialogsStore()
const dialogId = computed(() => route.params.id)

onMounted(async () => {
  await dialogs.fetchMessages(dialogId.value)
})
</script>

<template>
  <div class="container mt-5">
    <AppNavbar />
    <h1 class="title is-4">Диалог #{{ dialogId }}</h1>
    <Chat-ChatWindow :dialog-id="dialogId" />
  </div>
</template>
```

Админка

pages/admin/index.vue
```vue
<script setup>
definePageMeta({ middleware: ['auth', 'admin'] })
const {$api} = useNuxtApp()
const stats = ref(null)
const err = ref('')
onMounted(async () => {
  try {
    stats.value = await $api('/admin/stats')
  } catch (e) {
    err.value = 'Не удалось получить статистику'
  }
})
</script>

<template>
  <div class="container mt-5">
    <AppNavbar />
    <h1 class="title is-4">Админка — Статистика</h1>
    <div v-if="err" class="notification is-danger is-light">{{ err }}</div>
    <div class="columns" v-if="stats">
      <div class="column">
        <div class="box">
          <p class="title is-5">Пользователи</p>
          <p class="is-size-3">{{ stats.users_count ?? '—' }}</p>
        </div>
      </div>
      <div class="column">
        <div class="box">
          <p class="title is-5">Диалоги</p>
          <p class="is-size-3">{{ stats.dialogs_count ?? '—' }}</p>
        </div>
      </div>
      <div class="column">
        <div class="box">
          <p class="title is-5">Персонажи</p>
          <p class="is-size-3">{{ stats.characters_count ?? '—' }}</p>
        </div>
      </div>
    </div>
    <NuxtLink to="/admin/users" class="button is-primary mt-3">Пользователи</NuxtLink>
  </div>
</template>
```

pages/admin/users/index.vue
```vue
<script setup>
definePageMeta({ middleware: ['auth', 'admin'] })
const {$api} = useNuxtApp()
const users = ref([])
const loading = ref(false)
const err = ref('')

async function load() {
  loading.value = true
  err.value = ''
  try {
    users.value = await $api('/admin/users')
  } catch (e) {
    err.value = 'Ошибка загрузки пользователей'
  } finally {
    loading.value = false
  }
}
onMounted(load)

async function blockUser(u) {
  if (!confirm(`Заблокировать пользователя ${u.username || u.email}?`)) return
  await $api(`/admin/users/${u.id}/block`, { method: 'POST' })
  await load()
}
</script>

<template>
  <div class="container mt-5">
    <AppNavbar />
    <h1 class="title is-4">Пользователи</h1>
    <div v-if="err" class="notification is-danger is-light">{{ err }}</div>
    <div class="box" v-for="u in users" :key="u.id">
      <div class="level">
        <div class="level-left">
          <div>
            <div class="has-text-weight-semibold">{{ u.username || u.email }}</div>
            <div class="is-size-7 has-text-grey">ID: {{ u.id }}</div>
          </div>
        </div>
        <div class="level-right">
          <NuxtLink :to="`/admin/users/${u.id}`" class="button is-small is-link">Открыть</NuxtLink>
          <button class="button is-small is-danger ml-2" @click="blockUser(u)">Блокировать</button>
        </div>
      </div>
    </div>
  </div>
</template>
```

pages/admin/users/[id].vue
```vue
<script setup>
definePageMeta({ middleware: ['auth', 'admin'] })
const route = useRoute()
const {$api} = useNuxtApp()
const info = ref(null)
const err = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  err.value = ''
  try {
    info.value = await $api(`/admin/users/${route.params.id}`)
  } catch (e) {
    err.value = 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}
onMounted(load)

async function blockCharacter(id) {
  if (!confirm('Заблокировать персонажа?')) return
  await $api(`/characters/${id}/block`, { method: 'POST' })
  await load()
}
</script>

<template>
  <div class="container mt-5">
    <AppNavbar />
    <h1 class="title is-4">Пользователь #{{ $route.params.id }}</h1>
    <div v-if="err" class="notification is-danger is-light">{{ err }}</div>
    <div v-if="loading">Загрузка...</div>

    <div v-if="info" class="content">
      <p>Дата регистрации: <strong>{{ new Date(info.registered_at || info.created_at || Date.now()).toLocaleString() }}</strong></p>

      <h2 class="title is-5 mt-5">Созданные персонажи</h2>
      <div class="columns is-multiline">
        <div class="column is-4" v-for="c in (info.characters || [])" :key="c.id">
          <div class="card">
            <div class="card-content">
              <p class="title is-6">{{ c.name }}</p>
              <div class="tags">
                <span class="tag" v-for="t in (c.interests || [])" :key="t">{{ t }}</span>
              </div>
              <div class="buttons">
                <NuxtLink :to="`/characters/${c.id}`" class="button is-small is-link">Открыть</NuxtLink>
                <button class="button is-small is-danger" @click="blockCharacter(c.id)">Блокировать</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <h2 class="title is-5 mt-5">Диалоги (короткий список)</h2>
      <div class="box" v-for="d in (info.dialogs || [])" :key="d.id">
        <div class="level">
          <div class="level-left">
            <div>
              <div class="has-text-weight-semibold">{{ d.character_name }}</div>
              <div class="is-size-7 has-text-grey">{{ new Date(d.created_at).toLocaleString() }}</div>
            </div>
          </div>
          <div class="level-right">
            <NuxtLink :to="`/admin/dialogs/${d.id}`" class="button is-small is-primary">Открыть</NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
```

pages/admin/dialogs/[id].vue
```vue
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
    <AppNavbar />
    <h1 class="title is-4">Диалог #{{ $route.params.id }}</h1>
    <div v-if="err" class="notification is-danger is-light">{{ err }}</div>
    <div class="chat-messages box">
      <Chat-MessageBubble v-for="(m, i) in msgs" :key="i" :message="m" />
    </div>
  </div>
</template>
```

Страница профиля (локальный bio/description, опционально)
Создайте pages/profile.vue, если нужно:
```vue
<script setup>
definePageMeta({ middleware: 'auth' })
const profile = useProfileStore()
</script>

<template>
  <div class="container mt-5">
    <AppNavbar />
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
```

Как работает чат
- Открываем /characters/:id — показываем контекст персонажа (как system bubble).
- Пользователь отправляет первое сообщение — фронт вызывает POST /dialogs/{character_id}/messages без dialog_id. Бэкенд создаёт диалог, возвращает dialog_id и ответ ассистента.
- После первого ответа фронт перенаправляет на /dialogs/:dialog_id для продолжения.

Админка
- /admin — показывает базовую статистику (GET /admin/stats).
- /admin/users — список пользователей (GET /admin/users), с кнопкой блокировки (POST /admin/users/{id}/block).
- /admin/users/:id — детали пользователя (GET /admin/users/{user_id}): дата регистрации, созданные персонажи (с возможностью блокировать каждого), и короткий список диалогов. Клик по диалогу — на /admin/dialogs/:id (GET /admin/dialogs/{dialog_id}).
- Блокировка персонажа: POST /characters/{id}/block.

ENV и запуск
- Установите зависимости и bulma.min.css положите в assets/css.
- В .env:
  - NUXT_PUBLIC_API_BASE=http://localhost:8000
- Запуск: npx nuxi dev

Заметки и расширяемость
- Схемы ответов API могут отличаться — в местах с res.message/res.assistant есть подстраховка. При необходимости подправьте поля под точную схему сервера.
- Профиль пользователя (bio/description) — сейчас локально; как появится серверный эндпоинт, перенесите в store с вызовами API.
- Для SSR можно сделать плагин api универсальным, но токен сейчас подставляется client-side, что нормально для SPA-паттерна.
- Визуал расширяем за счёт Bulma и scoped-стилей; UI очень легко нарастить.

Если хотите, могу добавить:
- Фильтры/поиск по персонажам (пол/теги/рейтинг).
- Пагинацию.
- Отдельные уведомления (toast) без библиотек.
- Отложенную отправку/индикатор “печатает…”.