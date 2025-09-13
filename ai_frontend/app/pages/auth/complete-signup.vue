<script setup>
const route = useRoute()
const router = useRouter()
onMounted(() => {
  router.replace({ path: '/signup/complete', query: route.query })
})
</script>

<template>
  <div class="container mt-5">
    <div class="notification is-link is-light">Перенаправление…</div>
  </div>
</template>