<template>
  <div class="unlogged-home">
    <h1>欢迎来到 PolyMetric</h1>
    <el-button type="primary" @click="$router.push('/login')">登录</el-button>
    <el-button @click="$router.push('/register')">注册</el-button>
  </div>
</template>

<style scoped>
.unlogged-home { text-align: center; padding: 100px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
</style>