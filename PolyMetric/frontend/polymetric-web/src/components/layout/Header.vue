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
        <el-menu-item @click="changePasswordDialog = true">修改密码</el-menu-item>
        <el-menu-item @click="handleLogout">退出登录</el-menu-item>
      </el-menu>
      <template #footer>
        <el-button @click="showMenu = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码子弹窗 -->
    <el-dialog v-model="changePasswordDialog" title="修改密码" width="400px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入旧密码" show-password clearable />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码（至少8位）" show-password clearable />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" placeholder="请确认新密码" show-password clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="changePasswordDialog = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="savePassword">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoPlay, ArrowDown } from '@element-plus/icons-vue'
import { changePassword, logout } from '@/api/users'  // ✅ 使用封装的 API

const router = useRouter()
const showMenu = ref(false)
const changePasswordDialog = ref(false)  // ✅ 重命名避免与函数冲突
const loading = ref(false)  // 加载状态
const username = localStorage.getItem('username') || 'User_name'
const passwordFormRef = ref(null)

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const checkConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: checkConfirmPassword, trigger: 'blur' }
  ]
}


const handleLogout = async () => {
  try {
    const refresh = localStorage.getItem('refresh')
    if (refresh) {
      await logout(refresh)  // 调用后端使 refresh token 失效
    }
  } catch (error) {
    // 即使后端调用失败，也继续清除本地数据
    console.warn('logout API failed:', error)
  } finally {
    localStorage.clear()
    ElMessage.success('退出成功')
    router.push('/login')
    showMenu.value = false
  }
}


const savePassword = () => {
  passwordFormRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.error('请输入正确信息')
      return
    }
    
    loading.value = true
    try {
      const res = await changePassword({
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password
      })
      
      // 成功处理
      ElMessage.success('密码修改成功，请重新登录')
      // 清空表单
      passwordForm.old_password = ''
      passwordForm.new_password = ''
      passwordForm.confirm_password = ''
      // 关闭弹窗
      changePasswordDialog.value = false
      showMenu.value = false
      
      // 强制重新登录：清除本地凭证，跳转登录页
      localStorage.clear()
      router.push('/login')
      
    } catch (error) {
      // 更详细的错误处理
      if (error.response?.status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        localStorage.clear()
        router.push('/login')
      } else if (error.response?.status === 400) {
        ElMessage.error('旧密码错误')
      } else {
        ElMessage.error(error.response?.data?.msg || '修改失败，请稍后重试')
      }
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.header { 
  height: 60px; 
  background: #fff; 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 0 30px; 
  box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
  position: fixed; 
  top: 0; 
  left: 0; 
  right: 0; 
  z-index: 1000; 
}
.logo { 
  font-size: 24px; 
  font-weight: bold; 
  color: #1890ff; 
  display: flex; 
  align-items: center; 
  gap: 10px; 
}
.user-info { 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  cursor: pointer; 
  padding-right: 20px; 
}
.username { 
  color: #333; 
  font-size: 16px; 
}
</style>
