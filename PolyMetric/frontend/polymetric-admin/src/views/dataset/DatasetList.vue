<template>
  <div class="dataset-list">
    <div class="header">
      <h3>所有数据集</h3>
      <div>
        <el-input placeholder="筛选" style="width: 200px; margin-right: 10px;" />
        <el-button type="primary">筛选</el-button>
      </div>
    </div>

    <el-table :data="datasets" style="margin-top: 20px;">
      <el-table-column prop="name" label="数据集名称" />
      <el-table-column prop="uploader" label="上传者" />
      <el-table-column prop="time" label="上传时间" />
      <el-table-column prop="type" label="类别" />
      <el-table-column label="操作">
        <template #default>
          <el-button type="danger" size="small">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
const datasets = [
  { name: 'dataset1', uploader: 'wang', time: '123', type: 'math' }
]
</script>