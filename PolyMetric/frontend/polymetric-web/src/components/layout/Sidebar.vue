<template>
  <div class="sidebar">
    <el-menu :default-active="$route.path" router background-color="#2c3e50" text-color="#fff" active-text-color="#409eff">
      <el-menu-item index="/home">
        <el-icon><House /></el-icon>
        <span>首页</span>
      </el-menu-item>
      <el-menu-item index="/datasets">
        <el-icon><Document /></el-icon>
        <span>数据集</span>
      </el-menu-item>
      <el-menu-item index="/evaluation">
        <el-icon><Cpu /></el-icon>
        <span>评测</span>
      </el-menu-item>
      <el-menu-item index="/leaderboard">
        <el-icon><Trophy /></el-icon>
        <span>排行榜</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { House, Document, Cpu, Trophy } from '@element-plus/icons-vue'
</script>

<style scoped>
.sidebar { width: 200px; height: calc(100vh - 60px); position: fixed; top: 60px; left: 0; overflow-y: auto; }
</style>