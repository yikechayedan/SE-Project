<template>
  <div class="forget">
    <h3>找回密码验证页面</h3>
    <el-form label-width="100px" style="max-width: 400px; margin: 0 auto;">
      <el-form-item label="邮箱">
        <el-input placeholder="输入邮箱" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" style="width: 100%;">发送验证码</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>
.forget { padding: 50px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
</style>