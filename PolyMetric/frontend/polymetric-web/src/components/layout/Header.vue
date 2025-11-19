<template>
  <div class="header">
    <div class="logo">
      <el-icon size="28"><VideoPlay /></el-icon>
      <span>PolyMetric</span>
    </div>
    <div class="user-info">
      <el-avatar :size="32" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
      <span class="username">{{ username }}</span>
      <el-dropdown>
        <el-icon size="18"><ArrowDown /></el-icon>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="$router.push('/profile')">个人主页</el-dropdown-item>
            <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { VideoPlay, ArrowDown } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = localStorage.getItem('username') || 'User_name'

const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
.header { height: 60px; background: #fff; display: flex; justify-content: space-between; align-items: center; padding: 0 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: fixed; width: 100%; z-index: 1000; }
.logo { font-size: 24px; font-weight: bold; color: #409eff; display: flex; align-items: center; gap: 10px; }
.user-info { display: flex; align-items: center; gap: 10px; }
.username { color: #333; font-size: 16px; }
</style>