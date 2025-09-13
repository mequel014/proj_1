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