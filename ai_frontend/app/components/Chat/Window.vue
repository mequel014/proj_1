<script setup>
const props = defineProps({
  character: { type: Object, default: null },
  dialogId: { type: [Number, String], default: null }
})

const dialogs = useDialogsStore()
const route = useRoute()
const router = useRouter()

const input = ref('')
const sending = ref(false)
const currentDialogId = ref(props.dialogId ? Number(props.dialogId) : null)

const msgs = computed(() => {
  const id = currentDialogId.value
  return (id ? dialogs.messages[id] : []) || []
})

const charId = computed(() => {
  if (props.character?.id) return Number(props.character.id)
  if (currentDialogId.value) return dialogs.dialogCharacter[currentDialogId.value] || null
  return null
})

onMounted(async () => {
  if (currentDialogId.value) {
    await Promise.all([
      dialogs.fetchMessages(currentDialogId.value),
      dialogs.ensureDialogCharacter(currentDialogId.value)
    ])
  }
})

async function send() {
  const text = input.value.trim()
  if (!text) return
  sending.value = true
  try {
    let characterId = charId.value
    if (!characterId && currentDialogId.value) {
      characterId = await dialogs.ensureDialogCharacter(currentDialogId.value)
    }
    if (!characterId) {
      throw new Error('character_id неизвестен')
    }

    const newId = await dialogs.sendMessage({
      characterId,
      text,
      dialogId: currentDialogId.value || null
    })
    input.value = ''

    if (!currentDialogId.value && newId) {
      currentDialogId.value = Number(newId)
      // если это страница персонажа — перейти на страницу диалога
      if (route.name?.toString().includes('characters-id')) {
        router.replace(`/dialogs/${newId}`)
      } else {
        await dialogs.fetchMessages(newId)
      }
    }
  } finally {
    sending.value = false
  }
}

const bottomRef = ref(null)

const scrollToBottom = async (smooth = true) => {
  await nextTick()
  bottomRef.value?.scrollIntoView({
    behavior: smooth ? 'smooth' : 'auto',
    block: 'end'
  })
}

// Скроллим при изменении количества сообщений (и при первом рендере)
watch(
  () => msgs.value.length,
  () => scrollToBottom(true),
  { immediate: true }
)

// Если нужно — можно скроллить и при смене диалога
watch(
  () => currentDialogId.value,
  () => scrollToBottom(false)
)
</script>

<template>
  <div class="chat-container">
    <div class="chat-messages">
      <ChatMessageBubble
        v-if="!currentDialogId && character?.context"
        :message="{ role: 'system', text: character.context }"
      />
      <ChatMessageBubble v-for="(m, i) in msgs" :key="i" :message="m" />
      <div ref="bottomRef" />
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
<style scoped>
.chat-messages {
  overflow-y: auto;
  /* фиксированная высота или flex-grow, чтобы был скролл */
  max-height: 100%;
}
</style>