<template>
  <div class="evaluation-hall">
    <div class="page-header">
      <div class="hero">
          <div class="title-row">
            <el-icon><Timer /></el-icon> 
            <h2>评测广场</h2>
          </div>
          <p class="subtitle">创建和参与测评任务，支持搜索与分类筛选。</p>
          <div class="hero-stats">
            <div class="stat-card">
              <div class="label">已创建</div>
              <div class="value">{{ evaluations.length }}</div>
              <div class="hint">任务数量</div>
            </div>
            <div class="stat-card">
              <div class="label">已创建</div>
              <div class="value">{{ yesterdayNewCount }}</div>
              <div class="hint">昨日新建</div>
            </div>
            <div class="stat-card">
              <div class="label">已创建</div>
              <div class="value">{{ MyEvaluations.length }}</div>
              <div class="hint">你的任务</div>
            </div>
          </div>
      </div>
    </div>

    <div class="tool-card">
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
    </div>

    <el-table :data="filteredEvaluations" v-loading="isTableLoading" border style="width: 100%; margin-bottom: 40px;">
      <el-table-column prop="initiator" label="发起人" show-overflow-tooltip/>
      <el-table-column prop="taskName" label="任务名称" show-overflow-tooltip/>
      <el-table-column prop="model" label="模型" show-overflow-tooltip>
        <template #default="{ row }">
              <div class="model-name overflow-container">
                <el-icon><Box /></el-icon>
                <span class="ellipsis-content">{{ row.myModel_name }}</span>
                <span v-if="row.method === 'adversarial'"class="ellipsis-content">| {{ row.myModel_2_name }}</span>
              </div>
            </template>
      </el-table-column>
      <el-table-column prop="dataset" label="使用数据集" >
        <template #default="{ row }">
              <div class="dataset-name overflow-container">
                <el-icon><Folder /></el-icon>
                <span class="ellipsis-content">{{ row.data }}</span>
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
          v-if="scope.row.method === 'objective' && scope.row.status === 'pending'" 
          type="success" 
          link 
          :loading="loadingTasks[scope.row.id]"
          @click="handleRunEvaluation(scope.row)"
        >
          启动自动评测
        </el-button>
        <el-button 
          v-if="(scope.row.method === 'subjective' || scope.row.method === 'adversarial') && scope.row.status === 'awaiting_human_judge'" 
          type="success" 
          link 
          @click="handleStartEvaluation(scope.row)"
        >
          人工测评
        </el-button>
        <el-button 
          v-if="(scope.row.method === 'subjective' || scope.row.method === 'adversarial') && scope.row.status === 'pending' && scope.row.type === 'model'" 
          type="success"
          link 
          :loading="loadingTasks[scope.row.id]"
          @click="handleRunEvaluation(scope.row)"
        >
          启动自动评测
        </el-button>
        <el-button
          v-if="(scope.row.method === 'subjective' || scope.row.method === 'adversarial') && scope.row.status === 'pending' && scope.row.type === 'human'" 
          type="success"
          link 
          :loading="loadingTasks[scope.row.id]"
          @click="handleRunEvaluation(scope.row)"
        >
          启动人工评测
        </el-button>
        <el-button 
          v-if="(scope.row.method === 'subjective' || scope.row.method === 'adversarial') && scope.row.status === 'completed'" 
          type="info"
          link 
          @click="handleViewEvaluation(scope.row)"
        >
          查看测评
        </el-button>
        <span 
          v-if="scope.row.status === 'running'"
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
import { getEvaluationTasks, runEvaluationTask } from '@/api/tasks.js'
import { getUserInfo } from '@/api/users.js'
import { el } from 'element-plus/es/locale/index.mjs'


const searchQuery = ref('')
const categoryFilter = ref('')
const currentPage = ref(1)
const pageSize = 5

const isTableLoading = ref(false)
const loadingTasks = ref({})
const showEvalDialog = ref(false)
const evaluations = ref([])
const MyEvaluations = ref([])
const router = useRouter()
// 获取昨天的日期字符串，例如 "2025-12-10"
const yesterdayDate = ref();
// 获取当前用户ID
const currentUserId = ref(null);

const filteredEvaluations = computed(() => {
  // 1. 根据搜索和分类条件进行过滤
  const filteredBySearchAndCategory = evaluations.value.filter(item => {
    // 确保 item 存在，并且相关属性不是 null/undefined
    if (!item) return false; // 添加对 item 本身的检查

    // 使用安全访问 (?. 或 || '') 确保属性存在且是字符串，防止对 undefined 调用 includes()
    const matchesSearch = (item.taskName || '').includes(searchQuery.value) || 
                          (item.model || '').includes(searchQuery.value) || 
                          (item.dataset || '').includes(searchQuery.value) || 
                          (item.initiator || '').includes(searchQuery.value);
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

// 重置筛选
const resetFilter = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
  currentPage.value = 1
  fetchAllTasks()
}

const formatTaskDisplay = (task) => {

    return {
        //保持api原有的id
        ...task,
        initiator: task.creator_username,
        taskName: task.name,
        model: task.myModel_name,
        data: task.dataset_name,
        type: task.judge_type,
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
    pending: '待启动',
    running: '进行中',
    completed: '已完成',
    awaiting_human_judge: '待评测',
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
    awaiting_human_judge: 'info'
  };
  return map[status] || '';
};

const getYesterdayDateString = () => {
    // 1. 获取当前日期
    const today = new Date();
    
    // 2. 将日期设置为前一天
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    
    // 3. 获取格式化的日期字符串
    yesterdayDate.value = yesterday.toLocaleDateString();
};

// 统计昨日新建任务数
const yesterdayNewCount = computed(() => {
    if (!evaluations.value || evaluations.value.length === 0) {
        return 0;
    }
    
    return evaluations.value.filter(task => {
        const taskDate = task.time ? task.time.substring(0, 10) : '';
        return taskDate === yesterdayDate.value;
    }).length;
});


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
        MyEvaluations.value = formattedTasks.filter(task => task.creator_username === localStorage.getItem('username'));
        
    } catch (error) {
        console.error('加载评测任务失败:', error);
        ElMessage.error(`加载评测任务失败: ${error.message}`);
    }
}

const fetchUserID = async () => {
    try {
        const response = await getUserInfo();
        const data = response.data.data;
        currentUserId.value = data.id;
    } catch (error) {
        console.error('获取用户信息失败:', error);
        ElMessage.error(`获取用户信息失败: ${error.message}`);
    }
}

/**
 * 动作处理函数
 */

// 处理每页条数变化
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1  // 切换每页条数时回到第一页
}

// 处理页码变化
const handlePageChange = (val) => {
  currentPage.value = val
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
      params: { taskId: task.id , reviewerId: currentUserId.value , modelId: task.myModel , datasetId: task.dataset}
    })
  } else if(task.method === 'adversarial'){
    router.push({
      name: 'AdversarialEval',
      params: { taskId: task.id , reviewerId: currentUserId.value, modelId: task.myModel, model2Id: task.myModel_2, datasetId: task.dataset}
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

const handleRunEvaluation = async (task) => {
    // 1. 立即给用户反馈（乐观更新）
    // 不需要转圈了，直接把状态改为 running，界面会立刻显示 "正在处理，请稍候"
    task.status = 'running'; 
    
    try {
        // 2. 发送请求给后端（虽然后端会卡很久，但前端界面已经变了）
        await runEvaluationTask(task.id);
        
        // 3. 后端终于跑完后，再拉取一次最新结果（可能是 completed）
        fetchAllTasks();
    } catch (error) {
        console.error('启动评测失败:', error);
        ElMessage.error(`启动失败: ${error.message}`);
        // 如果失败了，把状态改回去，或者重新拉取列表
        fetchAllTasks();
    }
}

const handleSubmit =() => {
  fetchAllTasks();
}

const handleLocalFilter = (val) => {
}

onMounted(() => {
  fetchAllTasks()
  getYesterdayDateString();
  fetchUserID();
})
</script>

<style scoped>
.evaluation-hall {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7ff 0%, #ffffff 50%, #f7fbff 100%);
  border-radius: 14px;
  box-shadow: 0 6px 24px rgba(31, 41, 61, 0.08);
  min-height: calc(100vh - 140px);
}

.page-header {
  display: flex;
  gap: 18px;
  align-items: stretch;
  margin-bottom: 16px;
}


.hero {
  flex: 1;
  background: linear-gradient(150deg, #403075 0%, #D62779 50%, #FFA93E 100%);
  color: #fff;
  border-radius: 14px;
  padding: 20px 22px;
  position: relative;
  overflow: hidden;
}

.hero::after {
  content: '';
  position: absolute;
  right: -60px;
  top: -40px;
  width: 180px;
  height: 180px;
  background: radial-gradient(circle, rgba(255,255,255,0.24), rgba(255,255,255,0));
  transform: rotate(-8deg);
}

.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.badge {
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.22);
  border-radius: 20px;
  padding: 4px 10px;
  font-size: 12px;
  letter-spacing: 1px;
}

.hero h2 {
  margin: 0;
  font-size: 22px;
}

.subtitle {
  margin: 4px 0 14px;
  color: rgba(255,255,255,0.92);
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.stat-card {
  background: rgba(255,255,255,0.16);
  border: 1px solid rgba(255,255,255,0.20);
  border-radius: 12px;
  padding: 10px 12px;
  backdrop-filter: blur(2px);
}

.stat-card .label {
  font-size: 12px;
  opacity: 0.9;
}

.stat-card .value {
  font-size: 22px;
  font-weight: 700;
  margin: 6px 0 2px;
}

.stat-card .hint {
  font-size: 12px;
  opacity: 0.8;
}

.tool-bar {
  background: #ffffff;
  border-radius: 12px;
  padding: 14px;
  padding-left: 24px;
  box-shadow: 0 8px 24px rgba(18, 38, 63, 0.06);
  margin-bottom: 14px;
}

.overflow-container {
    overflow: hidden; 
    display: flex; 
    align-items: center;
    gap: 8px; 
}

.ellipsis-content {
    white-space: nowrap; 
    overflow: hidden;    
    text-overflow: ellipsis; 
    flex: 1; 
    display: block; 
}

.overflow-container {
    overflow: hidden; 
    display: flex; 
    align-items: center;
    gap: 8px; 
}

.ellipsis-content {
    white-space: nowrap; 
    overflow: hidden;    
    text-overflow: ellipsis; 
    flex: 1; 
    display: block; 
}

.dataset-name {
  color: #409eff;
  font-weight: 500;
}

.model-name {
  color: #409eff;
  font-weight: 500;
}

.my-tasks-container {
  padding: 20px;
}

.action-bar { 
  display: flex;
  align-items: center;
  margin-bottom: 20px; 
}

/* 新增：容器样式，控制溢出和图标对齐 */
.overflow-container {
  display: flex;
  align-items: center;
  gap: 8px; /* 图标和文本之间的间隔 */
  overflow: hidden; /* 裁剪溢出内容 */
}

/* 新增：文本样式，实现省略号 */
.ellipsis-content {
  white-space: nowrap; 
  overflow: hidden;    
  text-overflow: ellipsis; 
  flex: 1; /* 确保它占据所有剩余空间 */
  display: block; 
}

.el-table th { background: #f5f7fa; color: #333; }

.action-bar { 
  display: flex;
  align-items: center;
  margin-bottom: 20px; 
}

/* 新增：容器样式，控制溢出和图标对齐 */
.overflow-container {
  display: flex;
  align-items: center;
  gap: 8px; /* 图标和文本之间的间隔 */
  overflow: hidden; /* 裁剪溢出内容 */
}

/* 新增：文本样式，实现省略号 */
.ellipsis-content {
  white-space: nowrap; 
  overflow: hidden;    
  text-overflow: ellipsis; 
  flex: 1; /* 确保它占据所有剩余空间 */
  display: block; 
}

.el-table th { background: #f5f7fa; color: #333; }
  

/* Table Dark Theme Overrides */
:deep(.el-table) {
  --el-table-bg-color: #161b22;
  --el-table-tr-bg-color: #161b22;
  --el-table-header-bg-color: #0d1117;
  --el-table-border-color: #30363d;
  --el-table-text-color: #c9d1d9;
  --el-table-header-text-color: #8b949e;
  --el-table-row-hover-bg-color: #1f2428;
}

:deep(.el-table__inner-wrapper::before) {
  background-color: #30363d;
}

:deep(.el-table th) {
  background-color: #0d1117 !important;
  color: #8b949e !important;
  border-bottom: 1px solid #30363d !important;
}

:deep(.el-table td) {
  border-bottom: 1px solid #30363d !important;
}

/* Pagination Dark Mode Override */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 15px 0;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: #1f6bff;
  color: #ffffff;
}

:deep(.el-pagination.is-background .el-pager li) {
  background-color: #161b22;
  color: #8b949e;
  border: 1px solid #30363d;
}

:deep(.el-pagination.is-background .btn-prev),
:deep(.el-pagination.is-background .btn-next) {
  background-color: #161b22;
  color: #8b949e;
  border: 1px solid #30363d;
}

/* Input/Select Dark Mode Overrides (if global not enough) */
:deep(.el-input__wrapper) {
  background-color: #0d1117;
  box-shadow: 0 0 0 1px #30363d inset;
}

:deep(.el-input__inner) {
  color: #c9d1d9;
}
</style>