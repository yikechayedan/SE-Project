<template>
  <div class="user-datasets">
    <h3>他人数据集管理</h3>
    <el-table :data="datasets">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="type" label="类型" />
      <el-table-column prop="date" label="日期" />
      <el-table-column label="操作">
        <template #default>
          <el-button size="small" type="info">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
const datasets = [
  { name: '数据集1', type: '类型1', date: '2025-01-01' },
  { name: '数据集2', type: '类型2', date: '2025-01-02' },
]
</script>

<style scoped>
.user-datasets { padding: 20px; }
</style>