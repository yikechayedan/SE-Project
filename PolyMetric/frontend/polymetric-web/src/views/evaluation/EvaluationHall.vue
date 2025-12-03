<template>
  <div class="evaluation-hall">
    <h2>评测页面</h2>
    <el-button type="primary" style="margin-bottom: 20px;" @click="showEvalDialog = true">添加评测</el-button>
    <el-input v-model="searchQuery" placeholder="搜索评测" prefix-icon="Search" style="width: 300px; margin-bottom: 20px;" />
    <el-table :data="filteredEvaluations" border style="width: 100%; margin-bottom: 40px;">
      <el-table-column prop="initiator" label="发起人" />
      <el-table-column prop="taskName" label="任务名称" />
      <el-table-column prop="dataset" label="使用数据集" />
      <el-table-column prop="method" label="测评方法" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="time" label="时间" />
      <el-table-column prop="operation" label="操作">
        <template #default="scope">
        <el-button 
          v-if="scope.row.status === '完成'" 
          type="primary" 
          link 
          @click="handleViewReport()"
        >
          查看报告
        </el-button>
        <el-button 
          v-else-if="scope.row.status === '待测评'" 
          type="success" 
          link 
          @click="handleStartEvaluation(scope.row)"
        >
          开始测评
        </el-button>
        <el-button 
          v-else-if="scope.row.status === '已测评'" 
          type="info"
          link 
          @click="handleViewEvaluation(scope.row)"
        >
          查看测评
        </el-button>
        <span v-else>
          {{ scope.row.status }}... 
        </span>
        </template>
      </el-table-column>
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
import { useRouter } from 'vue-router' 

const router = useRouter()
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = 5

const evaluations = ref([
  { initiator: 'wang', taskName: '任务1', dataset: '数学数据集', method: '客观评测', status: '进行中', time: '2025-01-01'},
  { initiator: 'ruan', taskName: '任务2', dataset: '视觉数据集', method: '客观评测', status: '完成', time: '2025-01-02'},
  { initiator: 'geng', taskName: '任务3', dataset: '视觉数据集', method: '主观评测', status: '待测评', time: '2025-01-03'},
  { initiator: 'oour', taskName: '任务4', dataset: '视觉数据集', method: '对抗评测', status: '已测评', time: '2025-01-04'},
  { initiator: 'li', taskName: '任务5', dataset: '默认数据集', method: '客观评测', status: '进行中', time: '2025-01-05' },
  { initiator: 'zhang', taskName: '任务6', dataset: '数学数据集', method: '主观评测', status: '已测评', time: '2025-01-06'},
  { initiator: 'chen', taskName: '任务7', dataset: '视觉数据集', method: '对抗评测', status: '待测评', time: '2025-01-07'},
  { initiator: 'sun', taskName: '任务8', dataset: '默认数据集', method: '客观评测', status: '完成', time: '2025-01-08'},
  { initiator: 'liu', taskName: '任务9', dataset: '数学数据集', method: '主观评测', status: '待测评', time: '2025-01-09' },
  { initiator: 'zhao', taskName: '任务10', dataset: '视觉数据集', method: '对抗评测', status: '已测评', time: '2025-01-10' },
  // 更多数据
])

const filteredEvaluations = computed(() => evaluations.value.filter(item => item.taskName.includes(searchQuery.value)).slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))

const myTasks = ref([
  { taskName: '我的任务1', status: '进行中' },
  { taskName: '我的任务2', status: '完成' },
])

const handleViewReport = () => {
  router.push({ 
    path: `/evaluation/report`, 
  })
}

const handleStartEvaluation = (task) => {
  if(task.method === '主观评测') {
    router.push({ path: `/evaluation/subjective` })
  } else if(task.method === '对抗评测'){
    router.push({ path: `/evaluation/adversarial` })
  }
}

const handleViewEvaluation = (task) => {
  if(task.method === '主观评测') {
    router.push({ path: `/evaluation/subjective-result` })
  } else if(task.method === '对抗评测'){
    router.push({ path: `/evaluation/adversarial-result` })
  }
}

const viewTask = () => ElMessage.info('查看任务详情')

const showEvalDialog = ref(false)
</script>

<style scoped>
.evaluation-hall { padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); height: 100%; }
.el-table th { background: #f5f7fa; color: #333; }
</style>