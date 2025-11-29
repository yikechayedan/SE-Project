<template>
  <div class="forget-container">
    <el-card class="forget-card" shadow="always">
      <h2 class="title">找回密码</h2>
      <p class="subtitle">请输入您的注册邮箱，我们将发送验证码</p>
      
      <el-form :model="form" :rules="rules" ref="formRef" label-width="0px">
        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            placeholder="请输入注册邮箱"
            size="large"
            prefix-icon="Message"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="code">
          <div class="code-row">
            <el-input
              v-model="form.code"
              placeholder="请输入验证码"
              size="large"
              prefix-icon="Key"
              maxlength="6"
              clearable
            />
            <el-button 
              type="primary" 
              size="large"
              :disabled="countdown > 0"
              :loading="sendingCode"
              @click="sendCode"
              class="send-btn"
            >
              {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            style="width: 100%;" 
            @click="verifyAndNext"
            :loading="verifying"
          >
            下一步
          </el-button>
        </el-form-item>
        
        <div class="links">
          <span @click="$router.push('/login')">返回登录</span>
          <span @click="$router.push('/register')">注册账号</span>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { sendResetCode, verifyResetCode } from '@/api/users'

const router = useRouter()
const formRef = ref(null)
const countdown = ref(0)
const sendingCode = ref(false)
const verifying = ref(false)
let timer = null

const form = reactive({
  email: '',
  code: ''
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '验证码为6位数字', trigger: 'blur' }
  ]
}

// 启动倒计时
const startCountdown = () => {
  countdown.value = 60
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

// 组件卸载时清除定时器
onUnmounted(() => {
  if (timer) clearInterval(timer)
})

// 发送验证码
const sendCode = async () => {
  // 先验证邮箱
  await formRef.value.validateField('email')
  
  sendingCode.value = true
  try {
    const res = await sendResetCode(form.email)
    if (res.data.code === 200 || res.status === 200) {
      ElMessage.success('验证码已发送到您的邮箱')
      startCountdown()
    } else {
      ElMessage.error(res.data.msg || '发送失败')
    }
  } catch (error) {
    if (error.response?.status === 404) {
      ElMessage.error('该邮箱未注册')
    } else {
      ElMessage.error(error.response?.data?.msg || '发送失败，请稍后重试')
    }
  } finally {
    sendingCode.value = false
  }
}

// 验证并跳转
const verifyAndNext = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      verifying.value = true
      try {
        const res = await verifyResetCode(form.email, form.code)
        if (res.data.code === 200 || res.status === 200) {
          ElMessage.success('验证成功')
          // 将邮箱和验证码存储，传递给重置页面
          sessionStorage.setItem('resetEmail', form.email)
          sessionStorage.setItem('resetCode', form.code)
          router.push('/reset')
        } else {
          ElMessage.error(res.data.msg || '验证码错误或已过期')
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.msg || '验证失败')
      } finally {
        verifying.value = false
      }
    }
  })
}
</script>

<style scoped>
.forget-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}

.forget-card {
  width: 420px;
  padding: 40px 30px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
  transition: transform 0.3s ease;
}

.forget-card:hover {
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

.code-row {
  display: flex;
  gap: 10px;
  width: 100%;
}

.code-row .el-input {
  flex: 1;
}

.send-btn {
  width: 120px;
  flex-shrink: 0;
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
