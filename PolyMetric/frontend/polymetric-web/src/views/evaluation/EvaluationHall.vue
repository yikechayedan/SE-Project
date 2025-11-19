<template>
  <div class="evaluation-hall">
    <h2>评测页面</h2>
    <el-button type="primary" style="margin-bottom: 20px;" @click="showEvalDialog = true">添加评测</el-button>
    <el-input v-model="searchQuery" placeholder="搜索评测" prefix-icon="Search" style="width: 300px; margin-bottom: 20px;" />
    <el-table :data="filteredEvaluations" border style="width: 100%; margin-bottom: 40px;">
      <el-table-column prop="initiator" label="发起人" />
      <el-table-column prop="taskName" label="任务名称" />
      <el-table-column prop="dataset" label="使用数据集" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="time" label="时间" />
      <el-table-column prop="completed" label="是否完成" />
    </el-table>
    <el-pagination background layout="prev, pager, next, total" :total="evaluations.length" :page-size="pageSize" v-model:current-page="currentPage" style="margin-bottom: 40px; text-align: center;" />

    <h3>我的评测任务合集</h3>
    <el-table :data="myTasks" border style="width: 100%;">
      <el-table-column prop="taskName" label="任务名称" />
      <el-table-column prop="status" label="状态" />
      <el-table-column label="操作">
        <template #default>
          <el-button size="small" type="info" @click="viewTask">查看</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 评测弹窗 -->
    <EvalDialog v-model:showDialog="showEvalDialog" @close="showEvalDialog = false" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import EvalDialog from '../../components/common/EvalDialog.vue'

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = 5

const evaluations = ref([
  { initiator: 'wang', taskName: '任务1', dataset: '数学数据集', status: '进行中', time: '2025-01-01', completed: '否' },
  { initiator: 'ruan', taskName: '任务2', dataset: '视觉数据集', status: '完成', time: '2025-01-02', completed: '是' },
  // 更多数据
])

const filteredEvaluations = computed(() => evaluations.value.filter(item => item.taskName.includes(searchQuery.value)).slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))

const myTasks = ref([
  { taskName: '我的任务1', status: '进行中' },
  { taskName: '我的任务2', status: '完成' },
])

const viewTask = () => ElMessage.info('查看任务详情')

const showEvalDialog = ref(false)
</script>

<style scoped>
.evaluation-hall { padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); height: 100%; }
.el-table th { background: #f5f7fa; color: #333; }
</style>