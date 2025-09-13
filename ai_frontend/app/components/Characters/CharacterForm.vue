<script setup>
const props = defineProps({
  model: { type: Object, default: () => ({}) },
  submitText: { type: String, default: 'Создать' }
})
const emit = defineEmits(['submit'])

const name = ref(props.model.name || '')
const gender = ref(props.model.gender || '')
const interests = ref(props.model.interests || [])
const bio = ref(props.model.bio || '')             // NEW
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
      bio: bio.value,                             // NEW
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
          <label class="label">Био</label>
          <textarea
            class="textarea"
            v-model="bio"
            rows="3"
            placeholder="Короткое описание персонажа, манера общения, факты"
          ></textarea>
          <p class="help">Кратко. Для расширенного описания используйте поле «Контекст» ниже.</p>
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