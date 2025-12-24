<template>
  <div class="register-container">
    <ParticleBackground />

    <div class="register-content">
      <el-card class="register-card" shadow="always">
        <div class="card-header">
          <h2 class="title">加入 PolyMetric</h2>
          <p class="desc">创建您的账号，开启 AI 评测之旅</p>
        </div>

        <el-form 
          :model="registerForm" 
          :rules="registerRules" 
          ref="registerFormRef" 
          size="large"
          class="register-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="用户名 (字母、数字)"
              prefix-icon="User"
              class="tech-input"
            />
          </el-form-item>
          <el-form-item prop="email">
            <el-input
              v-model="registerForm.email"
              placeholder="电子邮箱"
              prefix-icon="Message"
              class="tech-input"
            />
          </el-form-item>
          
          <el-form-item prop="code">
            <div style="display: flex; width: 100%; gap: 10px;">
              <el-input
                v-model="registerForm.code"
                placeholder="邮箱验证码"
                prefix-icon="Key"
                class="tech-input"
                maxlength="6"
              />
              <el-button 
                type="primary" 
                :disabled="countdown > 0" 
                :loading="codeLoading"
                @click="handleSendCode"
                class="code-btn"
              >
                {{ countdown > 0 ? `${countdown}s 后重试` : '发送验证码' }}
              </el-button>
            </div>
          </el-form-item>

          <el-form-item prop="phone">
            <el-input
              v-model="registerForm.phone"
              placeholder="手机号 (11位)"
              prefix-icon="Phone"
              maxlength="11"
              class="tech-input"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="设置密码 (至少8位)"
              prefix-icon="Lock"
              show-password
              class="tech-input"
            />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="确认密码"
              prefix-icon="Lock"
              show-password
              class="tech-input"
            />
          </el-form-item>
          
          <el-form-item class="agreement-item">
            <el-checkbox v-model="registerForm.agree" class="tech-checkbox">
              我同意 <span class="highlight">服务条款</span> 和 <span class="highlight">隐私政策</span>
            </el-checkbox>
          </el-form-item>

          <el-form-item>
            <el-button 
              type="success" 
              class="submit-btn" 
              :loading="loading"
              :disabled="!registerForm.agree"
              @click="handleRegister"
            >
              立即注册
            </el-button>
          </el-form-item>
        </el-form>

        <div class="card-footer">
          已有账号？ <span class="login-link" @click="$router.push('/login')">直接登录</span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Message, Phone, Lock, Key } from '@element-plus/icons-vue'
import { register, sendRegisterCode } from '@/api/users' 
// 引入新创建的粒子组件 
import ParticleBackground from '@/components/common/ParticleBackground.vue'

const router = useRouter()
const registerFormRef = ref(null)
const loading = ref(false)
const codeLoading = ref(false)
const countdown = ref(0)

const registerForm = reactive({
  username: '',
  email: '',
  code: '',
  phone: '',
  password: '',
  confirmPassword: '',
  agree: false
})

const checkPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '用户名不能为空', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '邮箱不能为空', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '验证码不能为空', trigger: 'blur' },
    { len: 6, message: '验证码长度应为6位', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '密码不能为空', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '确认密码不能为空', trigger: 'blur' },
    { validator: checkPassword, trigger: 'blur' }
  ]
}

const handleSendCode = async () => {
  // 只校验邮箱字段
  registerFormRef.value.validateField('email', async (valid) => {
    if (valid) {
      codeLoading.value = true
      try {
        const res = await sendRegisterCode(registerForm.email)
        // 检查后端返回的结构，根据文档应该是 { code: 200, msg: "..." }
        if (res.code === 200 || (res.data && res.data.code === 200)) {
           ElMessage.success('验证码已发送，请查收邮箱')
           countdown.value = 60
           const timer = setInterval(() => {
             countdown.value--
             if (countdown.value <= 0) {
               clearInterval(timer)
             }
           }, 1000)
        } else {
           ElMessage.error(res.msg || (res.data && res.data.msg) || '发送失败')
        }
      } catch (error) {
         const errorMsg = error.response?.data?.msg || '发送验证码失败，请重试'
         ElMessage.error(errorMsg)
      } finally {
        codeLoading.value = false
      }
    } else {
        ElMessage.warning('请先输入正确的邮箱地址')
    }
  })
}

const handleRegister = () => {
  registerFormRef.value.validate(async (valid) => {
    if (valid && registerForm.agree) {
      loading.value = true
      try {
        const res = await register({
          username: registerForm.username,
          password: registerForm.password,
          email: registerForm.email,
          phone: registerForm.phone,
          code: registerForm.code
        })
        const data = res.data || res // 兼容直接返回data的情况
        if (data.code === 200) {
          ElMessage.success('注册成功！请登录')
          router.push('/login')
        } else {
          // 优先显示后端返回的具体错误信息
          ElMessage.error(data.msg || '注册失败，请稍后重试')
        }
      } catch (error) {
        // 处理 HTTP 400 等错误状态码
        const errorMsg = error.response?.data?.msg || '网络连接错误，请检查网络设置'
        ElMessage.error(errorMsg)
      } finally {
        loading.value = false
      }
    } else {
      ElMessage.warning('请检查表单信息或同意协议')
    }
  })
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #0d1117;
  overflow: hidden;
  font-family: 'Inter', sans-serif;
  padding: 20px;
}

/* 同样移除原有的 .tech-bg 等背景样式 */

.register-content { position: relative; z-index: 10; width: 100%; max-width: 480px; animation: slideUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1); }

.register-card {
  background: rgba(22, 27, 34, 0.75) !important;
  backdrop-filter: blur(12px);
  border: 1px solid rgba(103, 194, 58, 0.2) !important;
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.6) !important;
  border-radius: 16px;
  padding: 10px 20px;
}

.card-header { text-align: center; margin-bottom: 25px; }
.title { color: #fff; font-size: 24px; margin: 0 0 8px 0; }
.desc { color: #8b949e; font-size: 14px; margin: 0; }

:deep(.tech-input .el-input__wrapper) { background-color: #0d1117; box-shadow: 0 0 0 1px #30363d inset; transition: all 0.3s; }
:deep(.tech-input .el-input__wrapper:hover), :deep(.tech-input .el-input__wrapper.is-focus) { box-shadow: 0 0 0 1px #67c23a inset !important; background-color: #0d1117; }
:deep(.tech-input .el-input__inner) { color: #fff; }
:deep(.tech-checkbox .el-checkbox__label) { color: #8b949e; }
.highlight { color: #67c23a; cursor: pointer; }

.submit-btn {
  width: 100%; height: 44px; font-size: 16px; font-weight: 600;
  background: linear-gradient(90deg, #67c23a, #529b2e); border: none;
  box-shadow: 0 4px 15px rgba(103, 194, 58, 0.3); transition: all 0.3s;
}
.submit-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(103, 194, 58, 0.4); }

.code-btn {
  background-color: #0d1117;
  border-color: #67c23a;
  color: #67c23a;
  font-weight: 500;
}
.code-btn:hover, .code-btn:focus {
  background-color: rgba(103, 194, 58, 0.1);
  border-color: #67c23a;
  color: #67c23a;
}
.code-btn.is-disabled {
  background-color: #0d1117;
  border-color: #30363d;
  color: #8b949e;
}

.card-footer { text-align: center; margin-top: 15px; color: #8b949e; font-size: 14px; }
.login-link { color: #67c23a; cursor: pointer; font-weight: 600; }
.login-link:hover { text-decoration: underline; }

@keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
</style>