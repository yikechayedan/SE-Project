<template>
  <div class="sidebar">
    <el-menu :default-active="$route.path" router background-color="#e6f7ff" text-color="#595959" active-text-color="#1890ff">
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
</script>

<style scoped>
.sidebar { width: 200px; height: calc(100vh - 60px); position: fixed; top: 60px; left: 0; overflow-y: auto; background: #e6f7ff; box-shadow: 2px 0 10px rgba(0,0,0,0.05); }
.el-menu-item:hover { background: #d9ecff; }
</style>