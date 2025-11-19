<template>
  <div class="dataset-square">
    <h2>数据集主页面</h2>
    <el-input v-model="searchQuery" placeholder="查询数据集名字" prefix-icon="Search" style="width: 300px; margin-bottom: 20px;" />
    <el-table :data="filteredDatasets" border style="width: 100%;">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="uploader" label="上传者" />
      <el-table-column prop="uploadTime" label="上传时间" />
      <el-table-column prop="followCount" label="关注数" />
      <el-table-column prop="downloadCount" label="下载量" />
      <el-table-column prop="remark" label="备注" />
    </el-table>
    <el-pagination background layout="prev, pager, next, total" :total="datasets.length" :page-size="pageSize" v-model:current-page="currentPage" style="margin-top: 20px; text-align: center;" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = 5

const datasets = ref([
  { name: '数据集1', uploader: 'wang', uploadTime: '2025-01-01', followCount: 100, downloadCount: 50, remark: '数学数据集' },
  { name: '数据集2', uploader: 'ruan', uploadTime: '2025-01-02', followCount: 200, downloadCount: 100, remark: '视觉数据集' },
  // 添加10-20条模拟数据以测试分页
])

const filteredDatasets = computed(() => datasets.value.filter(item => item.name.includes(searchQuery.value)).slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))
</script>

<style scoped>
.dataset-square { padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.el-table th { background: #f5f7fa; color: #333; }
</style>