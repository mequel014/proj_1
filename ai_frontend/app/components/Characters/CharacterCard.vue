<script setup>
const props = defineProps({
  character: { type: Object, required: true },
  mine: { type: Boolean, default: false }
})
const router = useRouter()
const config = useRuntimeConfig()

// function normalizeUrl(u) {
//   if (!u) return ''
//   const clean = u.replaceAll('\\', '/')
//   if (clean.startsWith('http')) return clean
//   // Добавляем базовый URL бэка (http://localhost:8000)
//   return `${config.public.apiBase}${clean}`
// }

function normalizeUrl(u) {
  if (!u) return ''
  const clean = String(u).replaceAll('\\', '/').trim()

  // Абсолютный URL
  if (/^https?:\/\//i.test(clean)) {
    try {
      const url = new URL(clean)
      const isLocalBackend =
        (url.hostname === 'localhost' && url.port === '8000') ||
        (url.hostname === '127.0.0.1' && url.port === '8000') ||
        url.hostname === 'backend'

      // Переводим локальные http://localhost:8000/... на прокси /api/...
      if (isLocalBackend) {
        return `/api${url.pathname}${url.search}${url.hash}`
      }

      // Для прочих http-ссылок пробуем апгрейдить на https
      if (url.protocol === 'http:') {
        url.protocol = 'https:'
        return url.toString()
      }
      return clean
    } catch {
      // падать не будем — обработаем ниже как относительный путь
    }
  }

  // Относительные пути к uploads ведём через /api
  if (clean.startsWith('/static/uploads/')) return `/api${clean}`
  if (clean.startsWith('static/uploads/')) return `/api/${clean}`

  // Иначе просто делаем абсолютным путём от текущего origin
  return clean.startsWith('/') ? clean : `/${clean}`
}

const photoSrc = computed(() => normalizeUrl(props.character.photo_url))

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
        <div class="media-left" v-if="photoSrc">
          <figure class="image is-64x64">
            <img :src="photoSrc" :alt="character.name" style="object-fit: cover;">
          </figure>
        </div>
        <div class="media-content">
          <p class="title has-text-white is-5">{{ character.name }}</p>
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