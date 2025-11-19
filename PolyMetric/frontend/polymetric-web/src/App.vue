<template>
  <div class="app">
    <Header v-if="isLoggedIn" />
    <div v-if="isLoggedIn" class="main-layout">
      <Sidebar />
      <div class="content">
        <router-view />
      </div>
    </div>
    <router-view v-else />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import Header from './components/layout/Header.vue'
import Sidebar from './components/layout/Sidebar.vue'

const isLoggedIn = computed(() => !!localStorage.getItem('token'))
</script>

<style>
.app { background: #1a1a1a; min-height: 100vh; }
.main-layout { display: flex; }
.content { margin-left: 200px; padding: 30px; width: 100%; }
</style>