<script setup>
definePageMeta({ middleware: 'auth' })
const d = useDialogsStore()
onMounted(() => d.fetchDialogs())
</script>

<template>
  <div class="container mt-5">
    <h1 class="title is-4">Мои диалоги</h1>
    <div class="box" v-for="dlg in d.dialogs" :key="dlg.id">
      <div class="level">
        <div class="level-left">
          <div>
            <div class="has-text-weight-semibold">{{ dlg.character_name || dlg.character?.name || 'Диалог' }}</div>
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