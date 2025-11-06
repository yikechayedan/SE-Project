<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <Sidebar />
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-title">PolyMetric 后台管理</div>
        <el-dropdown @command="handleCommand">
          <span class="el-dropdown-link">
            管理员 <el-icon><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ArrowDown } from '@element-plus/icons-vue'
import Sidebar from './Sidebar.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const handleCommand = (command) => {
  if (command === 'logout') {
    localStorage.removeItem('isLoggedIn')
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container { height: 100vh; }
.header {
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  font-weight: bold;
  font-size: 18px;
}
.el-dropdown-link { cursor: pointer; color: #409eff; }
</style>