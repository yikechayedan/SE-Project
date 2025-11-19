<template>
  <div class="app">
    <template v-if="isLoggedIn && !isPublicPage">
      <Header />
      <div class="main-layout">
        <Sidebar />
        <div class="content">
          <router-view />
        </div>
      </div>
    </template>
    <router-view v-else />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Header from './components/layout/Header.vue'
import Sidebar from './components/layout/Sidebar.vue'

const route = useRoute()
const isLoggedIn = computed(() => !!localStorage.getItem('token'))
const isPublicPage = computed(() => ['UnloggedHome', 'Login', 'Register', 'Forget', 'Reset'].includes(route.name))
</script>

<style>
.app { min-height: 100vh; display: flex; flex-direction: column; background: #f0f2f5; color: #333; font-family: 'Segoe UI', sans-serif; }
.main-layout { display: flex; flex: 1; }
.content { margin-left: 200px; padding: 30px; flex: 1; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
</style>