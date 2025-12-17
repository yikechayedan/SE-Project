<template>
  <div class="reset-container">
    <el-card class="reset-card" shadow="always">
      <h2 class="title">重置密码</h2>
      <p class="subtitle">请设置您的新密码</p>
      
      <el-form :model="form" :rules="rules" ref="formRef" label-width="0px">
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入新密码（至少8位）"
            size="large"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次确认新密码"
            size="large"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            style="width: 100%;" 
            @click="resetPassword"
            :loading="loading"
          >
            确认重置
          </el-button>
        </el-form-item>
        
        <div class="links">
          <span @click="$router.push('/forget')">上一步</span>
          <span @click="$router.push('/login')">返回登录</span>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { resetPassword as resetPasswordApi } from '@/api/users'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

// 从 sessionStorage 获取邮箱和验证码
const email = ref('')
const code = ref('')

onMounted(() => {
  email.value = sessionStorage.getItem('resetEmail') || ''
  code.value = sessionStorage.getItem('resetCode') || ''
  
  // 如果没有邮箱或验证码，跳回忘记密码页
  if (!email.value || !code.value) {
    ElMessage.warning('请先完成邮箱验证')
    router.push('/forget')
  }
})

const form = reactive({
  password: '',
  confirmPassword: ''
})

// 确认密码验证
const checkPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: checkPassword, trigger: 'blur' }
  ]
}

// 重置密码
const resetPassword = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await resetPasswordApi(email.value, code.value, form.password)
        if (res.data.code === 200 || res.status === 200) {
          ElMessage.success('密码重置成功！请使用新密码登录')
          // 清除 sessionStorage
          sessionStorage.removeItem('resetEmail')
          sessionStorage.removeItem('resetCode')
          router.push('/login')
        } else {
          ElMessage.error(res.data.msg || '重置失败，请稍后重试')
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.msg || '重置失败，请检查网络连接')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.reset-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}

.reset-card {
  width: 420px;
  padding: 40px 30px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
  transition: transform 0.3s ease;
}

.reset-card:hover {
  transform: translateY(-5px);
}

.title {
  text-align: center;
  color: #303133;
  margin-bottom: 10px;
  font-size: 28px;
  font-weight: bold;
}

.subtitle {
  text-align: center;
  color: #909399;
  margin-bottom: 30px;
  font-size: 14px;
}

.links {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #409eff;
  cursor: pointer;
}

.links span:hover {
  text-decoration: underline;
}
</style>
