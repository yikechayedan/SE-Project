<template>
  <div class="header">
    <div class="logo">
      <el-icon size="28"><VideoPlay /></el-icon>
      <span>PolyMetric</span>
    </div>

    <el-popover
      v-model:visible="showMenu"
      trigger="click"
      placement="bottom-end"
      :width="240"
      popper-class="user-menu-popover"
      :show-arrow="false"
      transition="el-zoom-in-top"
    >
      <template #reference>
        <div class="user-info" :class="{ 'active': showMenu }">
          <el-avatar :size="32" :src="avatarUrl" />
          <span class="username">{{ username }}</span>
          <el-icon size="18" class="arrow-icon"><ArrowDown /></el-icon>
        </div>
      </template>

      <!-- Popover Content -->
      <div class="user-menu-container">
        <div class="user-card-header">
          <div class="header-decoration"></div>
          <div class="avatar-wrapper">
            <el-avatar :size="56" :src="avatarUrl" class="menu-avatar" />
            <div class="status-indicator"></div>
          </div>
          <div class="user-details">
            <span class="username-large">{{ username }}</span>
            <div class="user-badge">
              <span class="badge-dot"></span> 在线
            </div>
          </div>
        </div>
        
        <div class="menu-list">
          <div class="menu-label">账户管理</div>
          <div class="menu-item" @click="openChangePassword">
            <div class="item-icon-bg"><el-icon><Lock /></el-icon></div>
            <div class="item-content">
              <span class="item-title">修改密码</span>
              <span class="item-desc">定期更新密码保护账户</span>
            </div>
            <el-icon class="arrow-right"><ArrowRight /></el-icon>
          </div>
          <div class="menu-divider"></div>
          <div class="menu-item logout-item" @click="handleLogout">
            <div class="item-icon-bg danger"><el-icon><SwitchButton /></el-icon></div>
            <span class="item-title">退出登录</span>
          </div>
        </div>
      </div>
    </el-popover>

    <!-- 修改密码子弹窗 -->
    <el-dialog 
      v-model="changePasswordDialog" 
      width="440px" 
      align-center 
      append-to-body
      class="tech-dialog-custom"
      :show-close="false"
      destroy-on-close
    >
      <div class="dialog-content-wrapper">
        <div class="dialog-header-custom">
          <div class="header-icon-bg">
            <el-icon><Key /></el-icon>
          </div>
          <div class="header-text">
            <h3>安全中心</h3>
            <p>更新您的账户密码以保护账号安全</p>
          </div>
          <button class="close-btn" @click="changePasswordDialog = false">
            <el-icon><Close /></el-icon>
          </button>
        </div>
        
        <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-position="top" class="tech-form">
          <el-form-item label="当前旧密码" prop="old_password">
            <el-input 
              v-model="passwordForm.old_password" 
              type="password" 
              placeholder="验证您的身份" 
              show-password 
              :prefix-icon="Lock"
            />
          </el-form-item>
          <el-form-item label="设置新密码" prop="new_password">
            <el-input 
              v-model="passwordForm.new_password" 
              type="password" 
              placeholder="8位以上，包含字母和数字" 
              show-password 
              :prefix-icon="Key"
            />
          </el-form-item>
          <el-form-item label="确认新密码" prop="confirm_password">
            <el-input 
              v-model="passwordForm.confirm_password" 
              type="password" 
              placeholder="再次输入新密码" 
              show-password 
              :prefix-icon="Key"
            />
          </el-form-item>
        </el-form>

        <div class="dialog-footer">
          <el-button @click="changePasswordDialog = false" class="cancel-btn">取消</el-button>
          <el-button type="primary" :loading="loading" @click="savePassword" class="save-btn">确认修改</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoPlay, ArrowDown, Lock, SwitchButton, Key, ArrowRight, Close } from '@element-plus/icons-vue'
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

const openChangePassword = () => {
  showMenu.value = false
  changePasswordDialog.value = true
}

const handleLogout = async () => {
  showMenu.value = false
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
  background: #0d1117;
  border-bottom: 1px solid #30363d;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.logo {
  font-family: 'Share Tech Mono', monospace;
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: color 0.2s;
}

.logo:hover {
  color: #409eff;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  color: #c9d1d9;
  transition: background-color 0.2s;
  user-select: none;
}

.user-info:hover, .user-info.active {
  background-color: #21262d;
}

.user-info .arrow-icon {
  color: #8b949e;
  transition: transform 0.2s;
}

.user-info.active .arrow-icon {
  transform: rotate(180deg);
}

.username {
  font-size: 14px;
  font-weight: 500;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* User Menu Styles */
.user-menu-container {
  display: flex;
  flex-direction: column;
  background: #161b22;
  min-width: 280px;
}

.user-card-header {
  position: relative;
  padding: 24px 20px 20px;
  background: linear-gradient(180deg, rgba(31, 41, 55, 0.5) 0%, rgba(22, 27, 34, 0) 100%);
  border-bottom: 1px solid #30363d;
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #409eff, #8e44ad);
}

.avatar-wrapper {
  position: relative;
}

.menu-avatar {
  background: #0d1117;
  border: 2px solid #30363d;
  padding: 2px; /* Inner ring effect */
  box-sizing: content-box;
}

.status-indicator {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  background-color: #238636;
  border: 2px solid #161b22;
  border-radius: 50%;
}

.user-details {
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
}

.username-large {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
}

.user-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #8b949e;
  background: rgba(110, 118, 129, 0.1);
  padding: 2px 8px;
  border-radius: 12px;
  width: fit-content;
  border: 1px solid #30363d;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background-color: #238636;
  border-radius: 50%;
  box-shadow: 0 0 5px rgba(35, 134, 54, 0.4);
}

.menu-list {
  padding: 12px;
}

.menu-label {
  font-size: 12px;
  color: #6e7681;
  margin: 0 0 8px 8px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 4px;
}

.menu-item:hover {
  background-color: rgba(64, 158, 255, 0.1);
  transform: translateX(4px);
}

.item-icon-bg {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background-color: #21262d;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8b949e;
  transition: all 0.2s;
}

.menu-item:hover .item-icon-bg {
  background-color: #409eff;
  color: #fff;
}

.item-icon-bg.danger {
  color: #f85149;
}

.menu-item.logout-item:hover .item-icon-bg.danger {
  background-color: #f85149;
  color: #fff;
}

.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: #c9d1d9;
}

.menu-item:hover .item-title {
  color: #fff;
}

.item-desc {
  font-size: 12px;
  color: #6e7681;
  margin-top: 2px;
}

.arrow-right {
  font-size: 14px;
  color: #484f58;
  transition: transform 0.2s;
}

.menu-item:hover .arrow-right {
  color: #8b949e;
  transform: translateX(2px);
}

.menu-divider {
  height: 1px;
  background: #30363d;
  margin: 8px 0;
}

/* Custom Dialog Header */
.dialog-header-custom {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 0;
}

.header-icon-bg {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #409eff, #2563eb);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.header-text h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.header-text p {
  margin: 4px 0 0;
  font-size: 13px;
  color: #8b949e;
}

/* Dialog Footer Buttons */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 10px;
}

.cancel-btn {
  background: transparent !important;
  border: 1px solid #30363d !important;
  color: #c9d1d9 !important;
}

.cancel-btn:hover {
  border-color: #8b949e !important;
  color: #fff !important;
}

.save-btn {
  padding: 10px 24px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* Global Form Tweaks inside Dialog */
:deep(.tech-form .el-form-item__label) {
  padding-bottom: 8px;
  font-weight: 500;
}

:deep(.tech-form .el-input__wrapper) {
  padding: 4px 12px;
}
</style>

<style>
/* --- FORCED GLOBAL STYLES FOR POPUP & DIALOG --- */

/* 1. User Menu Popover - The "No White Border" Fix */
.el-popover.user-menu-popover {
  background: #161b22 !important;
  border: 1px solid #30363d !important;
  border-radius: 12px !important;
  padding: 0 !important;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.6) !important;
  overflow: visible !important; /* Allow decoration to overlap if needed */
}

.user-menu-popover .el-popper__arrow {
  display: none !important;
}

/* 2. Custom Change Password Dialog */
.tech-dialog-custom {
  background: #161b22 !important;
  border: 1px solid #30363d !important;
  border-radius: 16px !important;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.7) !important;
  overflow: hidden !important;
  padding: 0 !important; /* Remove default element padding */
  --el-dialog-bg-color: #161b22;
}

.tech-dialog-custom .el-dialog__header {
  display: none !important; /* Hide default header completely */
}

.tech-dialog-custom .el-dialog__body {
  padding: 0 !important; /* Reset body padding */
  color: #c9d1d9 !important;
}

/* Internal Layout for Dialog */
.dialog-content-wrapper {
  padding: 32px;
  background: #161b22;
}

/* Custom Header inside Dialog */
.dialog-header-custom {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 32px;
  position: relative;
}

.header-icon-bg {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.2), rgba(64, 158, 255, 0.05));
  border: 1px solid rgba(64, 158, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
  font-size: 28px;
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.15);
}

.header-text h3 {
  margin: 0 0 6px 0;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}

.header-text p {
  margin: 0;
  font-size: 14px;
  color: #8b949e;
  line-height: 1.5;
}

.close-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  background: transparent;
  border: none;
  color: #484f58;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(248, 81, 73, 0.1);
  color: #f85149;
}

/* Form Styling */
.tech-form .el-form-item__label {
  color: #c9d1d9 !important;
  font-weight: 500 !important;
  padding-bottom: 8px !important;
}

.tech-form .el-input__wrapper {
  background-color: #0d1117 !important;
  box-shadow: 0 0 0 1px #30363d inset !important;
  border-radius: 8px !important;
  padding: 8px 12px !important;
  transition: all 0.2s;
}

.tech-form .el-input__wrapper:hover, 
.tech-form .el-input__wrapper.is-focus {
  box-shadow: 0 0 0 1px #409eff inset, 0 0 0 3px rgba(64, 158, 255, 0.1) inset !important;
}

.tech-form .el-input__inner {
  color: #fff !important;
  height: 24px !important;
}

/* Footer Buttons */
.dialog-footer {
  margin-top: 32px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.dialog-footer .el-button {
  height: 40px;
  padding: 0 24px;
  border-radius: 8px;
  font-weight: 600;
}

.dialog-footer .cancel-btn {
  background: transparent !important;
  border: 1px solid #30363d !important;
  color: #c9d1d9 !important;
}

.dialog-footer .cancel-btn:hover {
  border-color: #8b949e !important;
  background: rgba(255,255,255,0.03) !important;
}

.dialog-footer .save-btn {
  background: #238636 !important; /* GitHub Green for primary actions */
  border: 1px solid #2ea043 !important;
  color: #fff !important;
  box-shadow: 0 4px 12px rgba(35, 134, 54, 0.2);
}

.dialog-footer .save-btn:hover {
  background: #2ea043 !important;
}
</style>