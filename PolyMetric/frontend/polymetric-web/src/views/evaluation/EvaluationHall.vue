<template>
  <div class="evaluation-hall">
    <h2>评测页面</h2>
    <el-button type="primary" style="margin-bottom: 20px;" @click="showEvalDialog = true">添加评测</el-button>
    <el-input v-model="searchQuery" placeholder="搜索评测" prefix-icon="Search" style="width: 300px; margin-bottom: 20px;" />
    <el-table :data="filteredEvaluations" border style="width: 100%; margin-bottom: 40px;">
      <el-table-column prop="initiator" label="发起人" />
      <el-table-column prop="taskName" label="任务名称" />
      <el-table-column prop="model" label="模型"/>
      <el-table-column prop="dataset" label="使用数据集" />
      <el-table-column prop="method" label="测评方法" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="time" label="时间" />
      <el-table-column label="操作">
        <template #default="scope">
        <el-button 
          v-if="scope.row.method === '客观评测' && scope.row.status === '完成'" 
          type="primary" 
          link 
          @click="handleViewReport(scope.row)"
        >
          查看报告
        </el-button>
        <el-button 
          v-else-if="(scope.row.method === '主观评测' || scope.row.method === '对抗评测') && scope.row.status === '待测评'" 
          type="success" 
          link 
          @click="handleStartEvaluation(scope.row)"
        >
          开始测评
        </el-button>
        <el-button 
          v-else-if="scope.row.status === '完成'" 
          type="info"
          link 
          @click="handleViewEvaluation(scope.row)"
        >
          查看测评
        </el-button>
        <span v-else>
          进行中... 
        </span>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination background layout="prev, pager, next, total" :total="evaluations.length" :page-size="pageSize" v-model:current-page="currentPage" style="margin-bottom: 40px; text-align: center;" />

    <h3>我的评测任务合集</h3>
    <el-table :data="myTasks" border style="width: 100%;">
      <el-table-column prop="taskName" label="任务名称" />
      <el-table-column prop="model" label="模型"/>
      <el-table-column prop="dataset" label="数据集" />
      <el-table-column prop="method" label="测评方法" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="time" label="时间" />
      <el-table-column label="操作">
        <template #default="scope">
        <el-button 
          v-if="scope.row.method === '客观评测' && scope.row.status === '完成'" 
          type="primary" 
          link 
          @click="handleViewReport(scope.row)"
        >
          查看报告
        </el-button>
        <el-button 
          v-else-if="(scope.row.method === '主观评测' || scope.row.method === '对抗评测') && scope.row.status === '待测评'" 
          type="success" 
          link 
          @click="handleStartEvaluation(scope.row)"
        >
          开始测评
        </el-button>
        <el-button 
          v-else-if="scope.row.status === '完成'" 
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

    <!-- 评测弹窗 -->
    <EvalDialog v-model:showDialog="showEvalDialog"
    @close="showEvalDialog = false"
    @task-submitted="handleSubmit()" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import EvalDialog from '../../components/common/EvalDialog.vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router' 
import { getEvaluationTasks } from '@/api/tasks.js'

//模拟api返回
// MOCK_API_RESPONSE: 模拟后端返回的 JSON 数据
const MOCK_API_RESPONSE = [
  { 
    "id": 101,
    "name": "GPT-4V 图像分类评测",
    "creator": 1, // 当前用户的任务
    "creator_username": "1",
    "dataset": 1,
    "dataset_name": "COCO 2017",
    "method": "objective", // 客观评测
    "status": "pending", // 待测评
    "created_at": "2025-11-30T10:00:00Z"
  },
  { 
    "id": 202,
    "name": "Gemini 文本生成评测",
    "creator": 1, // 当前用户的任务
    "creator_username": "123",
    "dataset": 2,
    "dataset_name": "CNN/Daily Mail",
    "method": "subjective", // 主观评测
    "status": "completed", // 完成
    "created_at": "2025-11-29T15:30:00Z"
  },
  { 
    "id": 303,
    "name": "Claude 3.5 逻辑推理对比",
    "creator": 2, // 其他用户的任务
    "creator_username": "123",
    "dataset": 3,
    "dataset_name": "Logic Bench",
    "method": "adversarial", // 对抗评测
    "status": "pending", // 待测评
    "created_at": "2025-12-01T08:00:00Z"
  },
  { 
    "id": 400,
    "name": "Mistral Code Review",
    "creator": 2, // 其他用户的任务
    "creator_username": "123",
    "dataset": 4,
    "dataset_name": "GitHub Code Snippets",
    "method": "objective",
    "status": "completed",
    "created_at": "2025-12-03T09:00:00Z"
  }
]

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = 5

const showEvalDialog = ref(false)
const evaluations = ref([])
const myTasks = ref([])
const router = useRouter()
const currentUsername = ref('')

const filteredEvaluations = computed(() => evaluations.value.filter(item => item.taskName.includes(searchQuery.value)).slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))

const formatTaskDisplay = (task) => {
    // 将 'objective', 'subjective', 'adversarial' 转换为中文
    const methodMap = {
        'objective': '客观评测',
        'subjective': '主观评测',
        'adversarial': '对抗评测',
    };
    
    // 将 'pending', 'running', 'completed' 等转换为中文
    const statusMap = {
        'pending': '待测评',
        'completed': '完成',
        'running': '进行中',
    };

    return {
        //保持api原有的id
        ...task,
        initiator: task.creator_username,
        taskName: task.name,
        model: task.myModel_name,
        dataset: task.dataset_name,
        method: methodMap[task.method] || task.method,
        status: statusMap[task.status] || task.status,
        time: task.created_at ? new Date(task.created_at).toLocaleDateString() : 'N/A',
    };
};

/**
 * 获取所有评测任务列表
 */
const fetchAllTasks = async () => {
    try {
        const response = await getEvaluationTasks();
        const data = response.data;
        // 1. 格式化所有任务并赋值给 evaluations
        const formattedTasks = data.map(formatTaskDisplay);
        evaluations.value = formattedTasks;
        
        // 2. 筛选出 "我的任务"
        const storedUsername = localStorage.getItem('username');
        if (storedUsername) {
            currentUsername.value = storedUsername;
        }
        myTasks.value = formattedTasks.filter(task => task.creator_username === currentUsername.value);

        ElMessage.success(`成功加载 ${data.length} 个评测任务。`);

    } catch (error) {
        console.error('加载评测任务失败:', error);
        ElMessage.error(`加载评测任务失败: ${error.message}`);
    }
}

const handleViewReport = (task) => {
  router.push({ 
    name: 'EvalReport', 
    params: { taskId: task.id }
  })
}

const handleStartEvaluation = (task) => {
  if(task.method === '主观评测') {
    router.push({
      name: 'SubjectiveEval',
      params: { taskId: task.id }
    })
  } else if(task.method === '对抗评测'){
    router.push({
      name: 'AdversarialEval',
      params: { taskId: task.id }
    })
  }
}

const handleViewEvaluation = (task) => {
  if(task.method === '主观评测') {
    router.push({ 
      name: 'SubjectResult',
      params: { taskId: task.id }
    })
  } else if(task.method === '对抗评测'){
    router.push({ 
      name: 'AdversarialResult',
      params: { taskId: task.id }
    })
  }
}

const handleSubmit =() => {
  fetchAllTasks();
}

onMounted(() => {
  fetchAllTasks()
})
</script>

<style scoped>
.evaluation-hall { padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); height: 100%; }
.el-table th { background: #f5f7fa; color: #333; }
</style>