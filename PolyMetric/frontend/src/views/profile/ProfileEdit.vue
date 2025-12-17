<template>
  <div class="profile-edit">
    <h3>个人信息编辑页面</h3>
    <el-form label-width="120px">
      <el-form-item label="头像">
        <el-upload action="#" list-type="picture-card" :auto-upload="false">
          <template #default>
            <el-icon><Plus /></el-icon>
          </template>
        </el-upload>
      </el-form-item>
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="介绍">
        <el-input type="textarea" v-model="form.intro" />
      </el-form-item>
      <el-form-item label="手机号">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary">保存</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'

const form = reactive({
  username: 'User_name',
  intro: '个人介绍',
  phone: '138xxxxxxx',
  email: 'example@163.com'
})
</script>

<style scoped>
.profile-edit { padding: 20px; max-width: 600px; margin: 0 auto; }
</style>