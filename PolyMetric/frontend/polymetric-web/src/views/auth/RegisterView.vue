<template>
  <div class="register">
    <h3>注册页面</h3>
    <el-form label-width="100px" style="max-width: 400px; margin: 0 auto;">
      <el-form-item label="用户名">
        <el-input placeholder="输入用户名" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input placeholder="输入邮箱" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input type="password" placeholder="输入密码" />
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input type="password" placeholder="确认密码" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" style="width: 100%;">注册</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>
.register { padding: 50px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
</style>