<template>
  <el-menu
    default-active="/dashboard"
    class="sidebar-menu"
    router
    background-color="#001529"
    text-color="#fff"
    active-text-color="#409eff"
  >
    <el-menu-item index="/dashboard">
      <el-icon><house /></el-icon>
      <span>仪表盘</span>
    </el-menu-item>
    <el-menu-item index="/user">
      <el-icon><user /></el-icon>
      <span>用户管理</span>
    </el-menu-item>
    <el-menu-item index="/dataset">
      <el-icon><document /></el-icon>
      <span>数据集管理</span>
    </el-menu-item>
    <el-menu-item index="/model">
      <el-icon><cpu /></el-icon>
      <span>模型展示</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { House, User, Document, Cpu } from '@element-plus/icons-vue'
</script>

<style scoped>
.sidebar-menu { height: 100vh; border-right: none; }
</style>