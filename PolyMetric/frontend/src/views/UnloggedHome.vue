<template>
  <div class="unlogged-home-container">
    <header class="unlogged-header">
      <div class="logo">
        <el-icon size="32" class="logo-icon"><Star /></el-icon>
        <span class="logo-text">PolyMetric</span>
      </div>
      <nav class="header-nav">
        <el-button type="primary" plain class="nav-button" @click="$router.push('/login')">登录</el-button>
      </nav>
    </header>

    <main class="hero-section">
      <h1 class="hero-title">欢迎来到 PolyMetric</h1>
      <p class="hero-subtitle">探索多模态大模型的能力边界</p>
      <div class="cta-buttons">
        <el-button type="primary" size="large" class="cta-button" @click="$router.push('/register')">立即注册</el-button>
        <el-button type="info" size="large" plain class="cta-button" @click="$router.push('/models')">查看模型榜单</el-button>
      </div>
    </main>

    <footer class="unlogged-footer">
      <p>&copy; 2025 PolyMetric. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup>
import { Star } from '@element-plus/icons-vue'
</script>

<style scoped>
:root {
  --primary-color: #409eff; /* Element UI Primary */
  --success-color: #67c23a; /* Element UI Success */
  --info-color: #909399;   /* Element UI Info */
  --bg-dark-start: #2c3e50; /* Dark blue-gray */
  --bg-dark-end: #34495e; /* Slightly lighter dark blue-gray */
  --text-light: #ecf0f1; /* Light gray */
  --text-muted: #bdc3c7; /* Muted gray */
  --accent-color: #3498db; /* Blue accent */
}

.unlogged-home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', sans-serif; /* Modern font */
  background: linear-gradient(135deg, var(--bg-dark-start), var(--bg-dark-end));
  background-size: 400% 400%;
  animation: gradientAnimation 15s ease infinite;
  color: var(--text-light);
  overflow: hidden; /* Prevent scrollbar from animation */
}

@keyframes gradientAnimation {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.unlogged-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 50px;
  background-color: rgba(0, 0, 0, 0.2); /* Slightly transparent dark header */
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  z-index: 10;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  color: var(--primary-color);
}

.logo-text {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-light);
  letter-spacing: 1px;
}

.header-nav .nav-button {
  border-radius: 20px;
  padding: 10px 25px;
  font-weight: bold;
  transition: all 0.3s ease;
}

.header-nav .nav-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
}

.hero-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 0 20px;
}

.hero-title {
  font-size: 64px;
  font-weight: 800;
  margin-bottom: 20px;
  letter-spacing: 2px;
  text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
  background: linear-gradient(45deg, #aafff0, #80ccff); /* Blue-green gradient for title */
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 24px;
  margin-bottom: 50px;
  color: var(--text-muted);
  max-width: 800px;
  line-height: 1.5;
}

.cta-buttons {
  display: flex;
  gap: 20px;
}

.cta-button {
  border-radius: 30px;
  padding: 15px 35px;
  font-size: 18px;
  font-weight: bold;
  text-transform: uppercase;
  transition: all 0.3s ease;
}

.cta-button:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.unlogged-footer {
  padding: 20px;
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
  background-color: rgba(0, 0, 0, 0.2);
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  z-index: 10;
}
</style>