<template>
  <div class="logged-home">
    <h1>已登录首页</h1>
    <p>欢迎回来，{{ username }}</p>
    <el-card>
      <h3>快速入口</h3>
      <el-button @click="$router.push('/datasets')">数据集</el-button>
      <el-button @click="$router.push('/evaluation')">评测</el-button>
    </el-card>
  </div>
</template>

<script setup>
const username = localStorage.getItem('username')
</script>

<style scoped>
.logged-home { padding: 20px; }
</style>