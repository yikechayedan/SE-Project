<template>
  <div class="models-view">
    <h2>模型页面</h2>
    <el-input v-model="searchQuery" placeholder="搜索模型" prefix-icon="Search" style="width: 300px; margin-bottom: 20px;" />
    <el-table :data="filteredModels" border style="width: 100%;">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="owner" label="所有者" />
      <el-table-column prop="params" label="参数量" />
      <el-table-column prop="type" label="类型" />
      <el-table-column prop="score" label="平均得分" />
    </el-table>
    <el-pagination background layout="prev, pager, next, total" :total="models.length" :page-size="pageSize" v-model:current-page="currentPage" style="margin-top: 20px; text-align: center;" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = 5

const models = ref([
  { name: '模型1', owner: 'OpenAI', params: '1.5T', type: '文本', score: '9.8' },
  { name: '模型2', owner: 'Google', params: '1T', type: '视觉', score: '9.5' },
  // 添加10-20条模拟数据以测试分页
])

const filteredModels = computed(() => models.value.filter(item => item.name.includes(searchQuery.value)).slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))
</script>

<style scoped>
.models-view { padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.el-table th { background: #f5f7fa; color: #333; }
</style>