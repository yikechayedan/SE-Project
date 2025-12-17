<template>
  <div class="login-container">
    <ParticleBackground />

    <div class="login-content">
      <el-card class="login-card" shadow="always">
        <div class="card-header">
          <div class="logo-area">
            <el-icon :size="40" color="#409eff"><VideoPlay /></el-icon>
          </div>
          <h2 class="title">PolyMetric <span class="subtitle">登录</span></h2>
          <p class="desc">多模态大模型能力评测平台</p>
        </div>

        <el-form :model="form" :rules="rules" ref="formRef" size="large" class="login-form">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              prefix-icon="User"
              class="tech-input"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              show-password
              class="tech-input"
            />
          </el-form-item>
          
          <div class="form-options">
            <el-checkbox v-model="form.remember" class="tech-checkbox">记住密码</el-checkbox>
            <span class="forgot-pwd" @click="$router.push('/forget')">忘记密码？</span>
          </div>

          <el-form-item>
            <el-button type="primary" class="submit-btn" :loading="loading" @click="login">
              立即登录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="card-footer">
          还没有账号？ <span class="register-link" @click="$router.push('/register')">立即注册</span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, VideoPlay } from '@element-plus/icons-vue'
import { login as loginApi } from '@/api/users'  
// 引入新创建的粒子组件
import ParticleBackground from '@/components/common/ParticleBackground.vue'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const login = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await loginApi({
          username: form.username,
          password: form.password
        })
        const data = res.data
        if (data.access) {
          localStorage.setItem('token', data.access)
          localStorage.setItem('refresh', data.refresh)
          localStorage.setItem('username', form.username)
          ElMessage.success('登录成功！')
          router.push('/home')
        } else {
          ElMessage.error('登录失败，请检查用户名或密码')
        }
      } catch (error) {
        ElMessage.error('登录失败：' + (error.response?.data?.detail || '网络错误'))
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #0d1117; /* 深色底，粒子在这个背景上显示 */
  overflow: hidden;
  font-family: 'Inter', sans-serif;
}

/* 移除原有的 .tech-bg, .tech-grid 等样式，因为已经被 Canvas 替代 */

/* --- 卡片样式 --- */
.login-content {
  position: relative;
  z-index: 10; /* 确保卡片在粒子之上 */
  animation: slideUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.login-card {
  width: 420px;
  background: rgba(22, 27, 34, 0.75) !important; /* 深色半透明 */
  backdrop-filter: blur(12px);
  border: 1px solid rgba(64, 158, 255, 0.2) !important;
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.6) !important;
  border-radius: 16px;
  padding: 20px;
}

.card-header { text-align: center; margin-bottom: 30px; }
.logo-area {
  margin-bottom: 15px; display: inline-block; padding: 12px;
  background: rgba(64, 158, 255, 0.1); border-radius: 50%;
  box-shadow: 0 0 15px rgba(64, 158, 255, 0.2);
}
.title { color: #fff; font-size: 26px; margin: 0; font-weight: 700; letter-spacing: 1px; }
.subtitle { color: #409eff; font-weight: 300; }
.desc { color: #8b949e; font-size: 14px; margin-top: 8px; }

/* --- 表单样式覆盖 --- */
:deep(.tech-input .el-input__wrapper) { background-color: #0d1117; box-shadow: 0 0 0 1px #30363d inset; transition: all 0.3s; }
:deep(.tech-input .el-input__wrapper:hover), :deep(.tech-input .el-input__wrapper.is-focus) { box-shadow: 0 0 0 1px #409eff inset !important; background-color: #0d1117; }
:deep(.tech-input .el-input__inner) { color: #fff; }
.form-options { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
:deep(.tech-checkbox .el-checkbox__label) { color: #8b949e; }
.forgot-pwd { color: #409eff; cursor: pointer; font-size: 14px; }
.forgot-pwd:hover { text-decoration: underline; }

.submit-btn {
  width: 100%; height: 44px; font-size: 16px; font-weight: 600;
  background: linear-gradient(90deg, #409eff, #2679ff); border: none;
  box-shadow: 0 4px 15px rgba(38, 121, 255, 0.3); transition: all 0.3s;
}
.submit-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(38, 121, 255, 0.4); }

.card-footer { text-align: center; margin-top: 20px; color: #8b949e; font-size: 14px; }
.register-link { color: #409eff; cursor: pointer; font-weight: 600; }
.register-link:hover { text-decoration: underline; }

@keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
</style>