<template>
  <div class="sidebar">
    <el-menu 
      :default-active="route.path" 
      router 
      class="tech-menu"
      background-color="transparent" 
      text-color="var(--text-primary)" 
      active-text-color="var(--accent-color)"
    >
      <el-menu-item index="/home">
        <el-icon><House /></el-icon>
        <span>首页</span>
      </el-menu-item>
      <el-menu-item index="/datasets">
        <el-icon><Document /></el-icon>
        <span>数据集</span>
      </el-menu-item>
      <el-menu-item index="/models">
        <el-icon><Cpu /></el-icon>
        <span>模型</span>
      </el-menu-item>
      <el-menu-item index="/evaluation">
        <el-icon><Timer /></el-icon>
        <span>评测</span>
      </el-menu-item>
      <el-menu-item index="/profile">
        <el-icon><User /></el-icon>
        <span>个人主页</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { House, Document, Cpu, Timer, User } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style scoped>
.sidebar {
  width: 220px;
  height: calc(100vh - 60px);
  position: fixed;
  top: 60px;
  left: 0;
  z-index: 999;
  background: #0d1117;
  border-right: 1px solid #30363d;
  padding: 12px 0;
  overflow-y: auto;
}

.tech-menu {
  border-right: none;
  background: transparent;
}

:deep(.el-menu-item) {
  margin: 4px 12px;
  border-radius: 6px;
  height: 40px;
  line-height: 40px;
  color: #8b949e;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

:deep(.el-menu-item:hover) {
  background-color: #161b22 !important;
  color: #c9d1d9 !important;
}

:deep(.el-menu-item.is-active) {
  background-color: #161b22 !important;
  color: #fff !important;
  border-left-color: #409eff;
  font-weight: 500;
}

:deep(.el-menu-item .el-icon) {
  font-size: 18px;
  margin-right: 12px;
  color: #8b949e;
  transition: color 0.2s;
}

:deep(.el-menu-item:hover .el-icon) {
  color: #c9d1d9;
}

:deep(.el-menu-item.is-active .el-icon) {
  color: #409eff !important;
}
</style>