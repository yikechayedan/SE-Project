<template>
  <div class="my-dataset-manage">
    <h3>个人数据集管理</h3>
    <el-button type="primary" style="margin-bottom: 20px;">上传数据集</el-button>
    <el-table :data="datasets">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="status" label="状态" />
      <el-table-column label="操作">
        <template #default>
          <el-button size="small" type="danger">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
const datasets = [
  { name: '我的数据集1', status: '活跃' },
  { name: '我的数据集2', status: '归档' },
]
</script>

<style scoped>
.my-dataset-manage { padding: 20px; }
</style>