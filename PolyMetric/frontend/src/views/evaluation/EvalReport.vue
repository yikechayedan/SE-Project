<template>
  <div class="report-detail">
    <div v-if="reportData && reportData.id" class="report-content">
      
      <h2 class="report-title">
        <el-icon><Document /></el-icon> 评测报告
      </h2>

      <el-divider class="title-divider" />

      <h3 class="section-title">📚 基础信息</h3>
      <el-row :gutter="20" class="meta-row">
        
        <el-col :span="8">
          <el-card shadow="hover" class="meta-item-card">
            <div class="meta-label">评测 ID</div>
            <div class="meta-value primary">{{ reportData.id }}</div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="hover" class="meta-item-card">
            <div class="meta-label">评测方法</div>
            <div class="meta-value info">{{ reportData.method == 'objective' ? '客观评测' : reportData.method }}</div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card shadow="hover" class="meta-item-card">
            <div class="meta-label">任务状态</div>
            <div class="meta-value status">
                <el-tag :type="reportData.status === 'completed' ? 'success' : 'info'" size="large" effect="dark">{{ reportData.status }}</el-tag>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-divider class="meta-divider" /> <el-row :gutter="20" class="summary-row">
        <el-col :span="12" :offset="6">
          <el-card shadow="hover" class="summary-card" :style="{ backgroundColor: getAccuracyColor(reportData.accuracy) }">
            <div class="summary-value">{{ formatAccuracy(reportData.accuracy) }}</div>
            <div class="summary-label">整体正确率 (Accuracy)</div>
          </el-card>
        </el-col>
      </el-row>

      <h3 class="section-title">📊 详细评测条目</h3>
      
      <el-table :data="paginatedItems" border stripe class="detail-table">
        <el-table-column prop="id" label="条目 ID" width="100" />
        <el-table-column prop="content" label="题目/条目名称" />
        <el-table-column prop="correct_answer" label="正确答案" width="150" />
        <el-table-column prop="predicted_answer" label="预测答案" width="150" />
        
        <el-table-column label="结果" width="100" align="center">
          <template #default="scope">
            <el-icon v-if="scope.row.is_correct === 1" class="result-icon correct-icon">
              <Check />
            </el-icon>
            <el-icon v-else class="result-icon incorrect-icon">
              <Close />
            </el-icon>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          background
          layout="prev, pager, next, total"
          :total="reportData.data.length"
          :page-size="pageSize"
          v-model:current-page="currentPage"
        />
      </div>
    </div>
    
    <el-empty v-else :description="errorMessage || '未找到评测报告'" />

  </div>
</template>

<script setup>
import { computed, ref, onMounted, defineProps } from 'vue'
import { Document, Check, Close } from '@element-plus/icons-vue'
import { getEvaluationTaskDetail } from '@/api/tasks.js'

const currentPage = ref(1)
const pageSize = 10

const props = defineProps({
    taskId: {
        type: Number,
        required: true
    }
})

// ===================== 响应式数据定义 (保持不变) =====================
const reportData = ref({
    id: null,
    method: '',
    status: '', 
    accuracy: null,
    data: [], 
});

const loading = ref(true); 
const errorMessage = ref(null); 

const paginatedItems = computed(() => {
    if (!reportData.value || !Array.isArray(reportData.value.data)) {
        return [];
    }
    const start = (currentPage.value - 1) * pageSize;
    const end = currentPage.value * pageSize;
    return reportData.value.data.slice(start, end);
});

// ===================== 辅助函数 (保持不变) =====================
const formatTime = (time) => {
  if (!time) return 'N/A'
  return new Date(time).toLocaleString('zh-CN', { 
    year: 'numeric', month: '2-digit', day: '2-digit', 
    hour: '2-digit', minute: '2-digit', second: '2-digit', 
    hour12: false 
  })
}

const formatAccuracy = (rate) => {
  if (rate === undefined || rate === null) return 'N/A'
  return `${(rate * 100).toFixed(2)}%`
}

const getAccuracyColor = (rate) => {
    if (rate >= 0.9) return '#E8F5E9'; // 高分浅绿
    if (rate >= 0.7) return '#FFFDE7'; // 中分浅黄
    return '#FFEBEE'; // 低分浅红
}

// ===================== 数据获取逻辑 (保持不变) =====================
const fetchReportData = async () => {
  loading.value = true;
  errorMessage.value = null;
  try{
    const response = await getEvaluationTaskDetail(props.taskId);

    if (response.data && response.data.id) {
        reportData.value = response.data;

        const status = reportData.value.status;
        if (status !== 'completed' && status !== 'error') {
          errorMessage.value = `评测任务状态为 ${status}，尚未完成。`;
          reportData.value.id = null; 
        }
    } else {
        errorMessage.value = '获取评测报告失败：返回数据为空或无效。';
        reportData.value.id = null; 
    }

  }catch(error){
    errorMessage.value = '获取评测报告时发生网络或服务器错误';
    console.error('获取评测报告错误:', error);
    reportData.value.id = null; 
  } finally {
      loading.value = false;
    }
}

onMounted(() => {
    fetchReportData();
})
</script>

<style scoped>
/* ======================== 报告容器和背景 ======================== */
.report-detail {
  padding: 40px; 
  background-color: var(--bg-body); 
  min-height: 100vh;
}

/* ======================== 标题和分割线 ======================== */
.report-title {
  display: flex;
  align-items: center;
  font-size: 32px; 
  font-weight: 600; 
  color: var(--text-primary); 
  margin-bottom: 5px;
}
.report-title .el-icon {
  margin-right: 12px;
  font-size: 36px;
  color: var(--el-color-primary);
}
.title-divider {
    margin-top: 15px;
    margin-bottom: 30px;
}

/* ======================== 基础信息卡片 (新样式) ======================== */
.meta-row {
    margin-bottom: 20px;
}
.meta-item-card {
    text-align: center;
    border-radius: 10px;
    height: 120px; /* 固定高度 */
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: all 0.3s ease;
    cursor: default;
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
}
.meta-item-card:hover {
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
    border-color: var(--el-color-primary-light-3);
}

.meta-label {
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 8px;
    font-weight: 500;
}

.meta-value {
    font-size: 28px; /* 增大数值字号 */
    font-weight: bold;
    line-height: 1.2;
}

.meta-value.primary {
    color: var(--el-color-primary); /* ID使用主色调 */
}

.meta-value.info {
    color: var(--el-color-info); /* 方法使用信息色调 */
}

.meta-value.status {
    height: 35px; /* 确保 Tag 居中 */
    display: flex;
    justify-content: center;
    align-items: center;
}

.meta-divider {
    margin-top: 20px;
    margin-bottom: 40px;
}


/* ======================== 统计概览卡片 (保持不变) ======================== */
.summary-row {
  margin-bottom: 40px; 
}
.summary-card {
  text-align: center;
  border-radius: 12px;
  transition: all 0.3s ease; 
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05); 
  border: 1px solid var(--border-color); /* Add border for dark mode visibility */
}

.summary-card:hover {
    transform: translateY(-5px); 
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}
.summary-card :deep(.el-card__body) {
    padding: 30px; 
    transition: background-color 0.3s;
}

.summary-value {
  font-size: 48px; 
  font-weight: 800;
  color: #1a2a3a; /* Consider adapting this if card background changes drastically */
  margin-bottom: 8px;
  line-height: 1;
}
.summary-label {
  font-size: 16px;
  color: #5f748c;
}

/* ======================== 详细条目表格和分页 (保持不变) ======================== */
.section-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
  padding-left: 5px;
}
.detail-table {
    border-radius: 8px;
    overflow: hidden; 
}
.detail-table :deep(.el-table__header-wrapper th) {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    font-weight: bold;
}

.pagination-container {
  margin-top: 25px;
  text-align: center;
  display: flex;
  justify-content: center;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: var(--el-color-primary);
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

/* ======================== 结果图标 (保持不变) ======================== */
.result-icon {
  font-size: 20px; 
  font-weight: bold;
}
.correct-icon {
  color: #67c23a;
}
.incorrect-icon {
  color: #f56c6c;
}

/* Descriptions Dark Mode Override */
:deep(.el-descriptions__label) {
  background-color: var(--bg-secondary) !important;
  color: var(--text-secondary) !important;
}

:deep(.el-descriptions__content) {
  background-color: var(--bg-body) !important;
  color: var(--text-primary) !important;
}

:deep(.el-descriptions__cell) {
  border-color: var(--border-color) !important;
}

:deep(.el-divider) {
  border-color: var(--border-color);
}
</style>