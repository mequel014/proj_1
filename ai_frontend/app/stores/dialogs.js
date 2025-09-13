import { defineStore } from 'pinia'

export const useDialogsStore = defineStore('dialogs', () => {
  const dialogs = ref([])
  const messages = ref({})
  const dialogCharacter = ref({})

  const { $api } = useNuxtApp()

  async function fetchDialogs() {
    const res = await $api('/dialogs')
    dialogs.value = res || []
    for (const d of dialogs.value) {
      const cid = d.character_id || d.character?.id
      if (d.id && cid) dialogCharacter.value[d.id] = Number(cid)
    }
    return res
  }

  async function fetchMessages(dialogId) {
    const res = await $api(`/dialogs/${dialogId}/messages`)
    messages.value[dialogId] = res || []
    return res
  }

  async function ensureDialogCharacter(dialogId) {
    const cached = dialogCharacter.value[dialogId]
    if (cached) return cached
    await fetchDialogs()
    return dialogCharacter.value[dialogId] || null
  }

  async function sendMessage({ characterId, text, dialogId = null }) {
    // 1) вычисляем правильный character_id
    let cid = characterId ? Number(characterId) : null
    if (!cid && dialogId) {
      cid = await ensureDialogCharacter(Number(dialogId))
      if (!cid) throw new Error('Не удалось определить character_id для диалога')
    }

    // 2) формируем тело запроса
    const body = { message: text }
    if (dialogId !== null && dialogId !== undefined && dialogId !== '' && !Number.isNaN(Number(dialogId))) {
      body.dialog_id = Number(dialogId)
    }

    // 3) отправляем
    const res = await $api(`/dialogs/${cid}/messages`, { method: 'POST', body })

    // 4) определяем id диалога
    const newDialogId = res.dialog_id ?? dialogId
    if (newDialogId && cid) {
      dialogCharacter.value[newDialogId] = Number(cid)
    }

    // 5) сразу отрисуем ваше сообщение
    if (!messages.value[newDialogId]) messages.value[newDialogId] = []
    messages.value[newDialogId].push({ role: 'user', text, created_at: new Date().toISOString() })

    // 6) пробуем достать ответ ассистента из ответа
    const assistantMsg =
      res.assistant ??
      res.reply ??
      res.answer ??
      res.message ??              // некоторые бэки кладут сюда ответ ассистента
      res.assistant_message ??    // ещё вариант названия поля
      null

    if (assistantMsg) {
      // добавим без доп. запроса
      messages.value[newDialogId].push(
        typeof assistantMsg === 'string'
          ? { role: 'assistant', text: assistantMsg }
          : { role: 'assistant', text: assistantMsg.text || assistantMsg.content || String(assistantMsg) }
      )
    } else {
      // 7) если ответ не пришёл в POST — подгружаем историю (это починит “видно только после обновления”)
      await fetchMessages(newDialogId)
    }

    // 8) если это новый диалог — обновим список диалогов
    if (!dialogId) await fetchDialogs()

    return newDialogId
  }

  return { dialogs, messages, dialogCharacter, fetchDialogs, fetchMessages, ensureDialogCharacter, sendMessage }
})