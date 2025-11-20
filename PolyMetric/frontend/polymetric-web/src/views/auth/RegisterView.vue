<template>
  <div class="register-container">
    <div class="register-wrapper">
      <h1 class="main-title">欢迎加入 PolyMetric</h1>
      <p class="sub-title">创建您的账号，开始探索数据世界</p>
      <el-form 
        :model="registerForm" 
        :rules="registerRules" 
        ref="registerFormRef" 
        class="register-form"
        label-position="top"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名（字母、数字组合）"
            size="large"
            clearable
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item label="邮箱地址" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入有效的邮箱地址"
            size="large"
            clearable
            prefix-icon="Message"
          />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="registerForm.phone"
            placeholder="请输入11位手机号"
            size="large"
            clearable
            prefix-icon="Phone"
            maxlength="11"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入至少8位密码"
            size="large"
            show-password
            clearable
            prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            size="large"
            show-password
            clearable
            prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item class="agreement-item">
          <el-checkbox v-model="registerForm.agree">我同意 PolyMetric 的服务条款和隐私政策</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            class="submit-btn" 
            :disabled="!registerForm.agree"
            @click="handleRegister"
          >
            立即注册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="footer-links">
        <span>已有账号？</span>
        <el-link type="primary" @click="$router.push('/login')">立即登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const registerFormRef = ref(null)

const registerForm = reactive({
  username: '',
  email: '',
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
  phone: [
    { required: true, message: '手机号不能为空', trigger: 'blur' },
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

const handleRegister = () => {
  registerFormRef.value.validate(async (valid) => {
    if (valid && registerForm.agree) {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/users/register/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: registerForm.username,
            password: registerForm.password,
            email: registerForm.email,
            phone: registerForm.phone
          })
        })
        const data = await response.json()
        if (data.code === 200) {
          ElMessage.success('注册成功！请登录')
          router.push('/login')
        } else {
          ElMessage.error('注册失败：' + (data.msg || '未知错误'))
        }
      } catch (error) {
        ElMessage.error('注册失败：网络错误')
      }
    } else {
      ElMessage.error('请检查表单信息或同意协议')
    }
  })
}
</script>

<style scoped>
.register-container {
  height: 100vh;
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}
.register-wrapper {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 16px;
  padding: 40px 32px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  text-align: center;
}
.main-title {
  font-size: 32px;
  color: #333;
  margin-bottom: 8px;
}
.sub-title {
  font-size: 16px;
  color: #666;
  margin-bottom: 32px;
}
.register-form {
  text-align: left;
}
.agreement-item {
  margin-bottom: 24px;
}
.submit-btn {
  width: 100%;
  font-size: 18px;
  border-radius: 8px;
}
.footer-links {
  margin-top: 16px;
  font-size: 14px;
  color: #666;
}
.footer-links .el-link {
  margin-left: 8px;
}
</style>