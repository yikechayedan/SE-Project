<template>
  <div class="header">
    <div class="logo">
      <el-icon size="28"><VideoPlay /></el-icon>
      <span>PolyMetric</span>
    </div>
    <div class="user-info" @click="showMenu = true">
      <el-avatar :size="32" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
      <span class="username">{{ username }}</span>
      <el-icon size="18"><ArrowDown /></el-icon>
    </div>

    <!-- 弹框 -->
    <el-dialog v-model="showMenu" title="用户菜单" width="300px" :close-on-click-modal="true">
      <el-menu>
        <el-menu-item @click="changePassword = true">修改密码</el-menu-item>
        <el-menu-item @click="logout">退出登录</el-menu-item>
      </el-menu>
      <template #footer>
        <el-button @click="showMenu = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码子弹窗 -->
    <el-dialog v-model="changePassword" title="修改密码" width="400px">
      <el-form label-width="100px">
        <el-form-item label="旧密码">
          <el-input type="password" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input type="password" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="changePassword = false">取消</el-button>
        <el-button type="primary" @click="savePassword">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoPlay, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const showMenu = ref(false)
const changePassword = ref(false)
const username = localStorage.getItem('username') || 'User_name'

const logout = () => {
  localStorage.clear()
  ElMessage.success('退出成功')
  router.push('/login')
  showMenu.value = false
}

const savePassword = () => {
  ElMessage.success('密码修改成功')
  changePassword.value = false
  showMenu.value = false
}
</script>

<style scoped>
.header { height: 60px; background: #fff; display: flex; justify-content: space-between; align-items: center; padding: 0 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: fixed; width: 100%; z-index: 1000; }
.logo { font-size: 24px; font-weight: bold; color: #1890ff; display: flex; align-items: center; gap: 10px; }
.user-info { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.username { color: #333; font-size: 16px; }
</style>