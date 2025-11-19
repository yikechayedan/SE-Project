<template>
  <div class="my-task-manage">
    <h3>个人任务管理页面</h3>
    <el-table :data="tasks">
      <el-table-column prop="name" label="任务名" />
      <el-table-column prop="status" label="状态" />
      <el-table-column label="操作">
        <template #default>
          <el-button size="small" type="info">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
const tasks = [
  { name: '任务1', status: '进行中' },
  { name: '任务2', status: '完成' },
]
</script>

<style scoped>
.my-task-manage { padding: 20px; }
</style>