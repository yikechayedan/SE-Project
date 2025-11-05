<template>
  <div class="user-list">
    <div class="header">
      <h3>用户管理</h3>
      <el-button type="primary">新建用户</el-button>
    </div>

    <el-table :data="users" style="margin-top: 20px;">
      <el-table-column prop="id" label="用户id" />
      <el-table-column prop="username" label="用户描述" />
      <el-table-column prop="phone" label="电话号码" />
      <el-table-column prop="email" label="电子邮箱" />
      <el-table-column label="操作">
        <template #default>
          <el-button size="small" type="success">修改</el-button>
          <el-button size="small" type="danger">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
const users = [
  { id: 'wang', username: 'ruan31', phone: '123', email: '123' }
]
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
</style>