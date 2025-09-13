<script setup>
import { ref } from 'vue'
const auth = useAuthStore()
auth.checkAdmin()
const router = useRouter()

const goHome = () => router.push('/')

// реактивный флаг, открыт ли бургерное меню
const isActive = ref(false)
const toggleMenu = () => {
  isActive.value = !isActive.value
}
</script>

<template>
  <nav class="navbar is-dark" role="navigation" aria-label="main navigation">
    <div class="navbar-brand">
      <a class="navbar-item" @click.prevent="goHome">🗨️ PersonaTalk</a>
      
      <!-- бургерное меню -->
      <a 
        role="button" 
        class="navbar-burger" 
        :class="{ 'is-active': isActive }"
        aria-label="menu" 
        :aria-expanded="isActive.toString()" 
        data-target="navMenu"
        @click="toggleMenu"
      >
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
      </a>
    </div>

    <!-- само меню -->
    <div 
      id="navMenu" 
      class="navbar-menu" 
      :class="{ 'is-active': isActive }"
    >
      <div class="navbar-start">
        <NuxtLink to="/characters" class="navbar-item" @click="toggleMenu">Персонажи</NuxtLink>
        <NuxtLink to="/dialogs" class="navbar-item" @click="toggleMenu" v-if="auth.isAuthenticated">Диалоги</NuxtLink>
        <NuxtLink to="/characters/mine" class="navbar-item" @click="toggleMenu" v-if="auth.isAuthenticated">Мои персонажи</NuxtLink>
        <NuxtLink to="/characters/new" class="navbar-item" @click="toggleMenu" v-if="auth.isAuthenticated">Создать</NuxtLink>
        <NuxtLink to="/admin" class="navbar-item" @click="toggleMenu" v-if="auth.isAdmin">Админка</NuxtLink>
      </div>
      <div class="navbar-end">
        <div class="navbar-item">
          <div class="buttons" v-if="!auth.isAuthenticated">
            <NuxtLink to="/signup" @click="toggleMenu" class="button is-primary">Регистрация</NuxtLink>
            <NuxtLink to="/login" @click="toggleMenu" class="button is-light">Войти</NuxtLink>
          </div>
          <div class="buttons" v-else>
            <NuxtLink to="/profile" class="button is-info is-light" title="Профиль">
              {{ auth.loginName || 'Профиль' }}
            </NuxtLink>
            <button class="button is-light" @click="auth.logout()">Выйти</button>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  background: #14182b;
  border-bottom: 1px solid #2b3050;
}
</style>