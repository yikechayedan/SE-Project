<template>
  <div class="dataset-square">
    <h3>数据集主页面</h3>
    <el-input placeholder="搜索数据集" prefix-icon="Search" style="margin-bottom: 20px; width: 300px;" />
    <el-row :gutter="20">
      <el-col :span="8" v-for="i in 6" :key="i">
        <el-card shadow="hover">
          <h4>数据集{{ i }}</h4>
          <p>描述: 示例数据集</p>
          <el-button type="primary" plain>下载</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.dataset-square { padding: 20px; }
</style>