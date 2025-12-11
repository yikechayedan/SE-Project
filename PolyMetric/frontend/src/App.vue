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
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import Header from './components/layout/Header.vue'
import Sidebar from './components/layout/Sidebar.vue'

const route = useRoute()

// 使用 ref 来存储登录状态，使其响应式
const tokenValue = ref(localStorage.getItem('token'))

// 监听路由变化，每次路由切换时重新检查 token
watch(
  () => route.path,
  () => {
    tokenValue.value = localStorage.getItem('token')
  },
  { immediate: true }
)

const isLoggedIn = computed(() => !!tokenValue.value)
const isPublicPage = computed(() => ['UnloggedHome', 'Login', 'Register', 'Forget', 'Reset'].includes(route.name))
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
.app { min-height: 100vh; display: flex; flex-direction: column; background: #f0f2f5; color: #333; font-family: 'Segoe UI', sans-serif; }
.main-layout { display: flex; flex: 1; margin-top: 60px; }
.content { margin-left: 200px; padding: 20px; flex: 1; min-height: calc(100vh - 60px); overflow-y: auto; }
</style>
