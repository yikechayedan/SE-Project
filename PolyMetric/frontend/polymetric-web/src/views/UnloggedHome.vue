<template>
  <div class="unlogged-home">
    <div class="header">
      <div class="logo">
        <el-icon size="28"><VideoPlay /></el-icon>
        <span>PolyMetric</span>
      </div>
      <el-button type="primary" plain @click="$router.push('/login')">登录</el-button>
    </div>
    <div class="content">
      <h1>欢迎来到 PolyMetric</h1>
      <p>多模态大模型能力评测平台</p>
      <el-button type="success" size="large" @click="$router.push('/register')">注册账号</el-button>
    </div>
  </div>
</template>

<style scoped>
.unlogged-home { height: 100vh; background: linear-gradient(135deg, #e6f7ff, #bae7ff); display: flex; flex-direction: column; }
.header { height: 60px; display: flex; justify-content: space-between; align-items: center; padding: 0 30px; background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.logo { font-size: 24px; font-weight: bold; color: #1890ff; display: flex; align-items: center; gap: 10px; }
.content { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #333; }
h1 { font-size: 48px; margin-bottom: 20px; }
p { font-size: 20px; margin-bottom: 40px; color: #666; }
</style>