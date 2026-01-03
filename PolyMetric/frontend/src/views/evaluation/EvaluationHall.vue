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
        <el-select v-model="creatorFilter" placeholder="创建者" style="width: 120px; margin-left: 15px;">
          <el-option label="我的任务" value="mine" />
          <el-option label="全部任务" value="all" />
        </el-select>

        <el-select v-model="categoryFilter" placeholder="评测方法" clearable style="width: 130px; margin-left: 15px;">
          <el-option label="客观评测" value="objective" />
          <el-option label="主观评测" value="subjective" />
          <el-option label="对抗评测" value="adversarial" />
        </el-select>

        <el-select v-model="judgeTypeFilter" v-if="categoryFilter !== 'objective'" placeholder="评测方式" clearable style="width: 130px; margin-left: 15px;">
          <el-option label="模型评测" value="model" />
          <el-option label="人工评测" value="human" />
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
      <el-table-column prop="dataset" label="使用数据集" show-overflow-tooltip>
        <template #default="{ row }">
              <div class="dataset-name overflow-container">
                <el-icon><Folder /></el-icon>
                <span class="ellipsis-content">{{ row.data }}</span>
              </div>
            </template>
      </el-table-column>
      <el-table-column prop="method" label="评测类型" width="100">
        <template #default="scope">
          <el-tag :type="getMethodTag(scope.row.method)" size="small">
            {{ formatMethod(scope.row.method) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="judge_type" label="评测方式" width="100">
        <template #default="scope">
          <el-tag :type="getTypeTag(scope.row.judge_type)" size="small">
            {{ formatType(scope.row.judge_type) }}
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
      <el-table-column prop="time" label="创建时间" width="120"/>
      <el-table-column prop="update" label="更新时间" width="120"/>
      <el-table-column label="操作">
        <template #default="scope">
          <div class="action-container">
            <el-button 
              v-if="scope.row.status === 'completed'" 
              type="primary" class="custom-action-btn" size="small"
              @click="scope.row.method === 'objective' ? handleViewReport(scope.row) : handleViewEvaluation(scope.row)"
            >
              <el-icon><Document /></el-icon><span>查看结果</span>
            </el-button>

            <el-button 
              v-if="scope.row.status === 'pending'" 
              type="success" class="custom-action-btn" size="small"
              :loading="loadingTasks[scope.row.id]"
              :disabled="scope.row.creator !== currentUserId"
              @click="handleRunEvaluation(scope.row)"
            >
              <el-icon v-if="!loadingTasks[scope.row.id]"><VideoPlay /></el-icon>
              <span>{{ scope.row.type === 'human' ? '生成回答' : '启动自动评测' }}</span>
            </el-button>

            <el-button 
              v-if="scope.row.status === 'awaiting_human_judge' && scope.row.creator === currentUserId" 
              type="warning" class="custom-action-btn" size="small"
              @click="handleStartEvaluation(scope.row)"
            >
              <el-icon><EditPen /></el-icon><span>人工测评</span>
            </el-button>

            <div v-if="scope.row.status === 'running'" class="running-status-box">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>正在处理...</span>
            </div>
          </div>
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
import { computed, onMounted, onUnmounted,  ref, watch} from 'vue'
import EvalDialog from '../../components/common/EvalDialog.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Timer, Refresh, Document, VideoPlay, EditPen, Loading, } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router' 
import { getEvaluationTasks, runEvaluationTask } from '@/api/tasks.js'
import { getUserInfo } from '@/api/users.js'
import { el } from 'element-plus/es/locale/index.mjs'


const searchQuery = ref('') // 搜索框
const categoryFilter = ref('') // 评测类型
const judgeTypeFilter = ref('')  // 评测方式
const creatorFilter = ref('mine') // 创建者
const currentPage = ref(1)
const pageSize = ref(5)
const pollTimer = ref(null)

const isTableLoading = ref(false)
const loadingTasks = ref({})
const showEvalDialog = ref(false)
const evaluations = ref([])
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
                          (item.myModel_name || '').includes(searchQuery.value) || 
                          (item.myModel_2_name || '').includes(searchQuery.value) ||
                          (item.data || '').includes(searchQuery.value) || 
                          (item.initiator || '').includes(searchQuery.value);
    // 检查是否符合分类条件
    // 如果 categoryFilter 为空字符串 ('')，表示“全部分类”，即所有都符合
    const matchesCategory = !categoryFilter.value || (item.method === categoryFilter.value);
    
    // 评测方式过滤
    const matchesJudgeType = !judgeTypeFilter.value || (item.type === judgeTypeFilter.value);

    //  创建者过滤 (我的/全部)
    const matchesCreator = creatorFilter.value === 'all' || (item.creator === currentUserId.value);
    
    return matchesSearch && matchesCategory && matchesJudgeType && matchesCreator;
  })

  // 2. 在过滤后的数组上进行分页操作
  const start = (currentPage.value - 1) * pageSize.value
  const end = currentPage.value * pageSize.value
  
  return filteredBySearchAndCategory.slice(start, end)
})

// 监听筛选条件变化，重置到第一页
watch([searchQuery, categoryFilter, judgeTypeFilter, creatorFilter], () => {
  currentPage.value = 1
})

// 重置筛选
const resetFilter = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
  judgeTypeFilter.value = ''
  creatorFilter.value = 'mine'
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
        type: task.method === 'objective' ? 'model' : task.judge_type,
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

const formatType = (type) => {
  const map = {
    model: '模型评测',
    human: '人工评测',
  };
  return map[type] || type;
};

const getTypeTag = (method) => {
  const map = {
    model: 'success',
    human: 'warning',
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

const MyEvaluations = computed(() => {
  if (!currentUserId.value || !evaluations.value) return [];
  return evaluations.value.filter(item => item.creator === currentUserId.value);
});


/**
 * 获取所有评测任务列表
 */
const fetchAllTasks = async (isSilent = false) => {
    if (!isSilent) isTableLoading.value = true;
    try {
        const response = await getEvaluationTasks();
        const data = response.data;
        const formattedTasks = data.map(formatTaskDisplay);
        evaluations.value = formattedTasks;
        
        // 自动判断是否需要启动或停止轮询
        checkPollingNecessity();
    } catch (error) {
        console.error('加载评测任务失败:', error);
        if (!isSilent) ElMessage.error(`加载评测任务失败: ${error.message}`);
    } finally {
        if (!isSilent) isTableLoading.value = false;
    }
}

const checkPollingNecessity = () => {
    const hasActiveTask = evaluations.value.some(
        task => task.status === 'running' || task.status === 'pending'
    );

    if (hasActiveTask) {
        startPolling();
    } else {
        stopPolling();
    }
}

const startPolling = () => {
    if (pollTimer.value) return; // 避免重复启动
    console.log('检测到正在运行的任务，开启轮询...');
    pollTimer.value = setInterval(() => {
        fetchAllTasks(true); // 传入 true，实现无感知静默更新
    }, 5000); // 每 5 秒轮询一次
}

const stopPolling = () => {
    if (pollTimer.value) {
        clearInterval(pollTimer.value);
        pollTimer.value = null;
        console.log('所有任务已完成或停止，关闭轮询');
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
  if (task.method === 'objective') {
    router.push({ 
      name: 'EvalReport', 
      params: { taskId: task.id }
    })
  } else {
    handleViewEvaluation(task);
  }
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
   try {
        loadingTasks.value[task.id] = true;
        await ElMessageBox.confirm(
            `确认启动任务吗？ 启动后将不能改变评测所用的类型、模型和数据集`,
            '警告',
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning',
            }
        );
        await runEvaluationTask(task.id);
        ElMessage.success('正在尝试启动任务...');      
        startPolling(); 
        task.status = 'running';
        await new Promise(resolve => setTimeout(resolve, 1000));
        
    } catch (error) {
        console.error('启动评测失败:', error);
        ElMessage.error(`启动失败: ${error.message}`);
        // 如果失败了，把状态改回去，或者重新拉取列表
        fetchAllTasks();
    } finally {
      loadingTasks.value[task.id] = false;
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

onUnmounted(() => {
    stopPolling();
})
</script>

<style scoped>
.evaluation-hall {
  padding: 24px;
  background: var(--bg-body);
  border-radius: 14px;
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
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 14px;
  padding-left: 24px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  margin-bottom: 14px;
  border: 1px solid var(--border-color);
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
  color: var(--accent-color);
  font-weight: 500;
}

.model-name {
  color: var(--accent-color);
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

.action-container {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

/* 统一按钮基础样式 */
.custom-action-btn {
  border: none !important; /* 去掉边框，让背景更纯粹 */
  transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
  padding: 6px 10px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* 默认状态：赋予一个较浅的背景色 (使用 Element 的变色函数或透明度) */
.custom-action-btn.el-button--primary { background-color: #ecf5ff !important; color: #409eff !important; }
.custom-action-btn.el-button--success { background-color: #f0f9eb !important; color: #67c23a !important; }
.custom-action-btn.el-button--warning { background-color: #fdf6ec !important; color: #e6a23c !important; }
.custom-action-btn.el-button--danger  { background-color: #fef0f0 !important; color: #f56c6c !important; }

/* 悬停状态：颜色加深，背景变亮/变显眼 */
.custom-action-btn.el-button--primary:hover { background-color: #409eff !important; color: #ffffff !important; }
.custom-action-btn.el-button--success:hover { background-color: #67c23a !important; color: #ffffff !important; }
.custom-action-btn.el-button--warning:hover { background-color: #e6a23c !important; color: #ffffff !important; }
.custom-action-btn.el-button--danger:hover  { background-color: #f56c6c !important; color: #ffffff !important; }

/* 运行中状态的样式盒子 */
.running-status-box {
  background-color: #f4f4f5;
  color: #909399;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.custom-action-btn .el-icon {
  margin-right: 4px; /* 图标与文字的间距 */
}

/* Table Theme Overrides using variables */
:deep(.el-table) {
  --el-table-bg-color: var(--bg-secondary);
  --el-table-tr-bg-color: var(--bg-secondary);
  --el-table-header-bg-color: var(--bg-body);
  --el-table-border-color: var(--border-color);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-secondary);
  --el-table-row-hover-bg-color: var(--bg-hover);
}

:deep(.el-table__inner-wrapper::before) {
  background-color: var(--border-color);
}

:deep(.el-table th) {
  background-color: var(--bg-body) !important;
  color: var(--text-secondary) !important;
  border-bottom: 1px solid var(--border-color) !important;
}

:deep(.el-table td) {
  border-bottom: 1px solid var(--border-color) !important;
}

/* Pagination Theme Override */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 15px 0;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: var(--accent-color);
  color: #ffffff;
}

:deep(.el-pagination.is-background .el-pager li) {
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

:deep(.el-pagination.is-background .btn-prev),
:deep(.el-pagination.is-background .btn-next) {
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

/* Input/Select Theme Overrides */
:deep(.el-input__wrapper) {
  background-color: var(--bg-tertiary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

:deep(.el-input__inner) {
  color: var(--text-primary);
}
</style>