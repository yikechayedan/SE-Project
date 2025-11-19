<template>
  <div class="datasets">
    <div class="action-bar">
      <el-button type="primary" round>新建数据集</el-button>
    </div>
    <el-row :gutter="20">
      <el-col :span="8" v-for="i in 3" :key="i">
        <el-card shadow="hover">
          <el-icon><Folder /></el-icon>
          <span>Name{{ i }}</span>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.action-bar { margin-bottom: 20px; }
</style>