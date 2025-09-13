<script setup>
const route = useRoute()
const router = useRouter()
onMounted(() => {
  const token = route.params.token
  router.replace({ path: '/signup/complete', query: { token } })
})
</script>

<template>
  <div class="container mt-5">
    <div class="notification is-link is-light">Перенаправление на завершение регистрации…</div>
  </div>
</template>