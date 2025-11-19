<template>
  <div class="reset">
    <h3>找回密码重置页面</h3>
    <el-form label-width="100px" style="max-width: 400px; margin: 0 auto;">
      <el-form-item label="验证码">
        <el-input placeholder="输入验证码" />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input type="password" placeholder="输入新密码" />
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input type="password" placeholder="确认新密码" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" style="width: 100%;">重置密码</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>
.reset { padding: 50px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
</style>