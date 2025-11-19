<template>
  <div class="login-container">
    <el-card class="login-card" shadow="always">
      <h2 class="title">PolyMetric 登录</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="0px">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名 / 邮箱"
            size="large"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.remember">记住密码</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width:100%;" @click="login">立即登录</el-button>
        </el-form-item>
        <div class="links">
          <span @click="$router.push('/register')">注册账号</span>
          <span @click="$router.push('/forget')">忘记密码？</span>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref(null)

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
  formRef.value.validate((valid) => {
    if (valid) {
      // 模拟登录成功（后续接入后端API替换）
      localStorage.setItem('token', 'fake-jwt-token')
      localStorage.setItem('username', form.username)
      ElMessage.success('登录成功！')
      router.push('/home')  // 跳转到已登录首页
    } else {
      ElMessage.error('请输入正确信息')
    }
  })
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}
.login-card {
  width: 420px;
  padding: 40px 30px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
  transition: transform 0.3s ease;
}
.login-card:hover {
  transform: translateY(-5px);
}
.title {
  text-align: center;
  color: #303133;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: bold;
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