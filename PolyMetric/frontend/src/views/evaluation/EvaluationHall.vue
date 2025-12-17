<template>
  <div class="evaluation-hall">
    <div class="page-header">
      <h2>
        <el-icon><Timer /></el-icon>  
        评测广场
      </h2>
      <p class="subtitle">创建和参与测评任务，支持搜索与分类筛选</p>
    </div>

    <div class="tool-bar">
    <el-button type="primary"  @click="showEvalDialog = true">添加评测</el-button>
    <el-input v-model="searchQuery" placeholder="搜索评测" prefix-icon="Search" style="width: 300px; margin-left: 30px;" />
    <el-select 
        v-model="categoryFilter" 
        placeholder="选择分类" 
        clearable
        @change="handleLocalFilter"
        style="width: 150px; margin-left: 15px;"
      >
        <el-option label="全部分类" value="" />
        <el-option label="客观评测" value="objective" />
        <el-option label="主观评测" value="subjective" />
        <el-option label="对抗评测" value="adversarial" />
      </el-select>
      <el-button :icon="Refresh" @click="resetFilter" style="margin-left: 15px;">重置</el-button>
    </div>

    <el-table :data="filteredEvaluations" border style="width: 100%; margin-bottom: 40px;">
      <el-table-column prop="initiator" label="发起人" />
      <el-table-column prop="taskName" label="任务名称" />
      <el-table-column prop="model" label="模型">
        <template #default="{ row }">
              <div class="model-name">
                <el-icon><Box /></el-icon>
                <span>{{ row.myModel_name }}</span>
              </div>
            </template>
      </el-table-column>
      <el-table-column prop="dataset" label="使用数据集" >
        <template #default="{ row }">
              <div class="dataset-name">
                <el-icon><Folder /></el-icon>
                <span>{{ row.dataset_name }}</span>
              </div>
            </template>
      </el-table-column>
      <el-table-column prop="method" label="评测方法" width="100">
        <template #default="scope">
          <el-tag :type="getMethodTag(scope.row.method)" size="small">
            {{ formatMethod(scope.row.method) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusTag(scope.row.status)" size="small">
            {{ formatStatus(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="time" label="创建时间" width="100"/>
      <el-table-column prop="update" label="更新时间" width="100"/>
      <el-table-column label="操作">
        <template #default="scope">
        <el-button 
          v-if="scope.row.method === 'objective' && scope.row.status === 'completed'" 
          type="primary" 
          link 
          @click="handleViewReport(scope.row)"
        >
          查看报告
        </el-button>
        <el-button 
          v-else-if="(scope.row.method === 'subjective' || scope.row.method === 'adversarial') && scope.row.status === 'pending'" 
          type="success" 
          link 
          @click="handleStartEvaluation(scope.row)"
        >
          开始测评
        </el-button>
        <el-button 
          v-else-if="scope.row.status === 'completed'" 
          type="info"
          link 
          @click="handleViewEvaluation(scope.row)"
        >
          查看测评
        </el-button>
        <span 
          v-else
          style="color: #909399; font-size: 14px;">
          正在处理，请稍候 
        </span>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[5, 10, 20, 50]"
            :total="evaluations.length"
            :background="true"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>

    <!-- 评测弹窗 -->
    <EvalDialog v-model:showDialog="showEvalDialog"
    @close="showEvalDialog = false"
    @task-submitted="handleSubmit()" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch} from 'vue'
import EvalDialog from '../../components/common/EvalDialog.vue'
import { ElMessage } from 'element-plus'
import { Timer, Refresh } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router' 
import { getEvaluationTasks } from '@/api/tasks.js'


const searchQuery = ref('')
const categoryFilter = ref('')
const currentPage = ref(1)
const pageSize = 5

const showEvalDialog = ref(false)
const evaluations = ref([])
const router = useRouter()

const filteredEvaluations = computed(() => {
  // 1. 根据搜索和分类条件进行过滤
  const filteredBySearchAndCategory = evaluations.value.filter(item => {
    // 检查是否符合搜索条件
    const matchesSearch = item.taskName.includes(searchQuery.value) || 
                          item.model.includes(searchQuery.value) ||
                          item.dataset.includes(searchQuery.value) ||
                          item.initiator.includes(searchQuery.value)
    
    // 检查是否符合分类条件
    // 如果 categoryFilter 为空字符串 ('')，表示“全部分类”，即所有都符合
    const matchesCategory = !categoryFilter.value || (item.method === categoryFilter.value)
    
    return matchesSearch && matchesCategory
  })

  // 2. 在过滤后的数组上进行分页操作
  const start = (currentPage.value - 1) * pageSize
  const end = currentPage.value * pageSize
  
  return filteredBySearchAndCategory.slice(start, end)
})

// 监听筛选条件变化，重置到第一页
watch([searchQuery, categoryFilter], () => {
  currentPage.value = 1
})

// 本地筛选
const handleLocalFilter = () => {
  // 筛选由 computed 自动完成，页码重置由 watch 处理
}

// 重置筛选
const resetFilter = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
  currentPage.value = 1
  fetchAllTasks()
}

// 处理每页条数变化
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1  // 切换每页条数时回到第一页
}

// 处理页码变化
const handlePageChange = (val) => {
  currentPage.value = val
}

const formatTaskDisplay = (task) => {

    return {
        //保持api原有的id
        ...task,
        initiator: task.creator_username,
        taskName: task.name,
        model: task.myModel_name,
        dataset: task.dataset_name,
        time: task.created_at ? new Date(task.created_at).toLocaleDateString() : 'N/A',
        update: task.updated_at ? new Date(task.updated_at).toLocaleDateString() : 'N/A',
    };
};

const formatMethod = (method) => {
  const map = {
    objective: '客观评测',
    subjective: '主观评测',
    adversarial: '对抗评测',
  };
  return map[method] || method;
};

const getMethodTag = (method) => {
  const map = {
    objective: 'success',
    subjective: 'warning',
    adversarial: 'danger',
  };
  return map[method] || '';
};

const formatStatus = (status) => {
  const map = {
    pending: '待测评',
    running: '进行中',
    completed: '已完成',
    failed: '失败',
  };
  return map[status] || status;
};

const getStatusTag = (status) => {
  const map = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
  };
  return map[status] || '';
};

/**
 * 获取所有评测任务列表
 */
const fetchAllTasks = async () => {
    try {
        const response = await getEvaluationTasks();
        const data = response.data;
        // 格式化所有任务并赋值给 evaluations
        const formattedTasks = data.map(formatTaskDisplay);
        evaluations.value = formattedTasks;
        
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
  if(task.method === 'subjective') {
    router.push({
      name: 'SubjectiveEval',
      params: { taskId: task.id }
    })
  } else if(task.method === 'adversarial'){
    router.push({
      name: 'AdversarialEval',
      params: { taskId: task.id }
    })
  }
}

const handleViewEvaluation = (task) => {
  if(task.method === 'subjective') {
    router.push({ 
      name: 'SubjectResult',
      params: { taskId: task.id }
    })
  } else if(task.method === 'adversarial'){
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
.evaluation-hall {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  min-height: calc(100vh - 140px);
}

.page-header {
  margin-bottom: 25px;
}

.page-header h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  color: #303133;
}

.page-header .subtitle {
  color: #909399;
  font-size: 14px;
  margin-top: 8px;
}

.tool-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.dataset-name {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  font-weight: 500;
}

.model-name {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  font-weight: 500;
}

.el-table th { background: #f5f7fa; color: #333; }

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 15px 0;
}
</style>