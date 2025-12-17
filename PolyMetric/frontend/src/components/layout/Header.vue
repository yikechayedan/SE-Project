<template>
  <div class="header">
    <div class="logo">
      <el-icon size="28"><VideoPlay /></el-icon>
      <span>PolyMetric</span>
    </div>
    <div class="user-info" @click="showMenu = true">
      <el-avatar :size="32" :src="avatarUrl" />
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoPlay, ArrowDown } from '@element-plus/icons-vue'
import { changePassword, logout, getUserInfo } from '@/api/users'

const router = useRouter()
const showMenu = ref(false)
const changePasswordDialog = ref(false)
const loading = ref(false)
const username = ref(localStorage.getItem('username') || 'User_name')
const passwordFormRef = ref(null)
const userAvatar = ref('')

// 默认头像
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 后端基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:80'

// 处理头像URL，确保是完整路径
const getFullAvatarUrl = (avatar) => {
  if (!avatar) return ''
  // 如果已经是完整URL，直接返回
  if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
    return avatar
  }
  // 确保路径以 /media/ 开头
  let path = avatar
  if (!path.startsWith('/')) {
    path = '/' + path
  }
  if (!path.startsWith('/media/')) {
    path = '/media' + path
  }
  return `${API_BASE_URL}${path}`
}

// 计算头像 URL
const avatarUrl = computed(() => {
  const url = getFullAvatarUrl(userAvatar.value)
  return url || defaultAvatar
})

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

// 组件挂载时获取用户信息
onMounted(async () => {
  await fetchUserInfo()
})

// 获取用户信息（包括头像）
const fetchUserInfo = async () => {
  try {
    const res = await getUserInfo()
    
    // 处理后端返回的 { code, msg, data } 格式
    let userData = res.data
    if (res.data?.code === 200 && res.data?.data) {
      userData = res.data.data
    }
    
    // 更新用户名和头像
    if (userData.username) {
      username.value = userData.username
      localStorage.setItem('username', userData.username)
    }
    if (userData.avatar) {
      userAvatar.value = userData.avatar
      localStorage.setItem('avatar', userData.avatar)
    }
  } catch (error) {
    // 获取失败时使用本地缓存
    const cachedAvatar = localStorage.getItem('avatar')
    if (cachedAvatar) {
      userAvatar.value = cachedAvatar
    }
    console.warn('获取用户信息失败:', error)
  }
}

// 暴露刷新头像方法，供其他组件调用
const refreshAvatar = async () => {
  await fetchUserInfo()
}

// 通过 defineExpose 暴露给父组件
defineExpose({
  refreshAvatar
})

const handleLogout = async () => {
  try {
    const refresh = localStorage.getItem('refresh')
    if (refresh) {
      await logout(refresh)
    }
  } catch (error) {
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
      
      ElMessage.success('密码修改成功，请重新登录')
      passwordForm.old_password = ''
      passwordForm.new_password = ''
      passwordForm.confirm_password = ''
      changePasswordDialog.value = false
      showMenu.value = false
      
      localStorage.clear()
      router.push('/login')
      
    } catch (error) {
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
