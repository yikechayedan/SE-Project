<template>
  <div class="tasks">
    <div class="action-bar">
      <el-button type="primary" round>新建任务</el-button>
    </div>
    <el-table :data="tasks" style="background: transparent;">
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
.action-bar { margin-bottom: 20px; }
</style>