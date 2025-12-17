<template>
  <div class="app">
    <ParticleBackground />
    <template v-if="isLoggedIn && !isPublicPage">
      <Header class="app-header" />
      <div class="main-layout">
        <Sidebar class="app-sidebar" />
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
import ParticleBackground from './components/common/ParticleBackground.vue' // Import ParticleBackground

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
:root {
  --header-height: 60px;
  --sidebar-width: 220px;
}

.app {
  min-height: 100vh;
  background-color: var(--bg-color);
  position: relative;
  overflow: hidden;
}

/* Futuristic grid background */
.app::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(64, 158, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(64, 158, 255, 0.05) 1px, transparent 1px);
  background-size: 2rem 2rem;
  z-index: 0;
  opacity: 0.5;
}

#app > .particle-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1; /* Just above the grid */
}

.main-layout {
  display: flex;
  position: relative;
  z-index: 10;
  background: transparent; /* Ensure main layout is see-through */
}

.content {
  margin-top: var(--header-height);
  margin-left: var(--sidebar-width);
  padding: 24px;
  width: calc(100% - var(--sidebar-width));
  min-height: calc(100vh - var(--header-height));
  position: relative;
  z-index: 5;
  background-color: var(--bg-secondary); /* Ensure content area is dark */
}

.app-header {
  z-index: 100;
}

.app-sidebar {
  z-index: 99;
}
</style>
