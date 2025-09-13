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