<template>
  <div class="model-list">
    <div class="header">
      <h3>模型展示</h3>
      <div>
        <el-input placeholder="筛选" style="width: 200px; margin-right: 10px;" />
        <el-button type="primary">筛选</el-button>
      </div>
    </div>

    <el-table :data="models" style="margin-top: 20px;">
      <el-table-column prop="name" label="模型名称" />
      <el-table-column prop="owner" label="所有者" />
      <el-table-column prop="params" label="参数量级" />
    </el-table>
  </div>
</template>

<script setup>
const models = [
  { name: 'gpt5', owner: 'wang', params: 'xxxB' }
]
</script>