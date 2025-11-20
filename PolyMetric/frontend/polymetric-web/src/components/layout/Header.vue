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
        <el-button @click="changePassword = false">取消</el-button>
        <el-button type="primary" @click="savePassword">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoPlay, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const showMenu = ref(false)
const changePassword = ref(false)
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

const logout = () => {
  localStorage.clear()
  ElMessage.success('退出成功')
  router.push('/login')
  showMenu.value = false
}

const savePassword = () => {
  passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          ElMessage.error('请先登录')
          changePassword.value = false
          showMenu.value = false
          router.push('/login')
          return
        }
        const response = await fetch('http://127.0.0.1:8000/api/users/change_password/', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            old_password: passwordForm.old_password,
            new_password: passwordForm.new_password
          })
        })
        const data = await response.json()
        if (response.ok) {
          ElMessage.success('密码修改成功')
          passwordForm.old_password = ''
          passwordForm.new_password = ''
          passwordForm.confirm_password = ''
          changePassword.value = false
          showMenu.value = false
        } else {
          ElMessage.error('修改失败：' + (data.msg || '旧密码错误或其他问题'))
        }
      } catch (error) {
        ElMessage.error('网络错误')
      }
    } else {
      ElMessage.error('请输入正确信息')
    }
  })
}
</script>

<style scoped>
.header { height: 60px; background: #fff; display: flex; justify-content: space-between; align-items: center; padding: 0 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: fixed; width: 100%; z-index: 1000; }
.logo { font-size: 24px; font-weight: bold; color: #1890ff; display: flex; align-items: center; gap: 10px; }
.user-info { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.username { color: #333; font-size: 16px; }
</style>