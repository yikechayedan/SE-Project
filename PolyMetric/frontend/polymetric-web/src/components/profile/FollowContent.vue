<template>
  <div class="follow">
    <div class="action-bar">
      <el-button plain round>多选</el-button>
      <el-button type="primary" round>下载</el-button>
      <el-button type="warning" round>上传</el-button>
    </div>
    <div class="list">
      <el-card v-for="i in 3" :key="i" shadow="hover" style="margin-bottom: 15px;">
        <div class="item">
          <span>Name{{ i }}</span>
          <p>上次修改时间：2025/01/01 00:00</p>
          <el-icon><StarFilled /></el-icon>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { StarFilled } from '@element-plus/icons-vue'
</script>

<style scoped>
.action-bar { text-align: right; margin-bottom: 20px; }
.item { display: flex; justify-content: space-between; align-items: center; }
</style>