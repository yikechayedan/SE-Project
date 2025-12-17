<template>
  <div class="report-detail">
    <div v-if="reportData && reportData.id" class="report-content">
      <h2 class="report-title">
        <el-icon><Document /></el-icon> 评测报告：{{ reportData.name }}
      </h2>

      <el-divider />

      <el-card class="meta-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>基础信息</span>
          </div>
        </template>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="任务名称">{{ reportData.name }}</el-descriptions-item>
          <el-descriptions-item label="评测 ID">{{ reportData.id }}</el-descriptions-item>
          <el-descriptions-item label="模型">{{ reportData.model }}</el-descriptions-item>
          <el-descriptions-item label="数据集">{{ reportData.dataset }}</el-descriptions-item>
          <el-descriptions-item label="评测方法">{{ reportData.evaluation_method }}</el-descriptions-item>
          <el-descriptions-item label="评测时间">{{ formatTime(reportData.evaluation_time) }}</el-descriptions-item>
          <el-descriptions-item label="评测用时">{{ reportData.evaluation_duration }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-row :gutter="20" class="summary-row">
        <el-col :span="6">
          <el-card shadow="hover" class="summary-card">
            <div class="summary-value">{{ reportData.summary.total_count }}</div>
            <div class="summary-label">测试数量</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="summary-card">
            <div class="summary-value">{{ reportData.summary.correct_count }}/{{ reportData.summary.total_count }}</div>
            <div class="summary-label">正确个数</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="summary-card" :body-style="{ background: getAccuracyColor(reportData.summary.accuracy_rate) }">
            <div class="summary-value">{{ formatAccuracy(reportData.summary.accuracy_rate) }}</div>
            <div class="summary-label">正确率</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="summary-card">
            <div class="summary-value score-value">{{ reportData.summary.score }}</div>
            <div class="summary-label">得分</div>
          </el-card>
        </el-col>
      </el-row>

      <h3 class="section-title">详细评测条目</h3>
      <el-table :data="paginatedItems" border stripe>
        <el-table-column prop="id" label="条目 ID" width="100" />
        <el-table-column prop="name" label="题目/条目名称" />
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
          :total="fullItemList.length"
          :page-size="pageSize"
          v-model:current-page="currentPage"
        />
      </div>
    </div>
    
    <el-empty v-else description="未找到评测报告" />

  </div>
</template>

<script setup>
import { computed, ref, onMounted, defineProps } from 'vue'
import { Document, Check, Close } from '@element-plus/icons-vue'
import { getEvaluationTaskDetail } from '@/api/tasks.js'

const currentPage = ref(1)
const pageSize = 10

//接收任务中的路由ID
const props = defineProps({
    taskId: {
        type: String, // ID 可能是字符串或数字
        required: true
    }
})

// ===================== 模拟数据定义 (静态数据) =====================


const reportData = ref({
    // 任务基础信息
    id: null,
    name: '',
    description: '',
    creator: null,
    creator_username: '',
    
    // 关联信息
    dataset: null,
    dataset_name: '',
    model: null,
    model_name: '',

    // 状态与结果
    method: '',
    status: 'pending',
    accuracy: null,
    score: null,
    
    // 时间信息
    created_at: '',
    updated_at: '',
    time_used: null,

    // 嵌套的评测条目列表（最重要，必须是空数组）
    data: [], 
});

const loading = ref(true); // 用于加载状态
const errorMessage = ref(null); // 用于错误信息

// 格式化时间函数（示例）
// ===================== 辅助函数 =====================

/**
 * 格式化时间戳
 */
const formatTime = (time) => {
  if (!time) return 'N/A'
  return new Date(time).toLocaleString('zh-CN', { 
    year: 'numeric', month: '2-digit', day: '2-digit', 
    hour: '2-digit', minute: '2-digit', second: '2-digit', 
    hour12: false 
  })
}

/**
 * 格式化准确率 (0.82 -> 82.00%)
 */
const formatAccuracy = (rate) => {
  if (rate === undefined || rate === null) return 'N/A'
  return `${(rate * 100).toFixed(2)}%`
}

/**
 * 根据准确率返回卡片背景颜色（仅用于演示）
 */
const getAccuracyColor = (rate) => {
    if (rate >= 0.9) return 'rgba(103, 194, 58, 0.15)'; // 高分绿色
    if (rate >= 0.7) return 'rgba(230, 162, 60, 0.15)'; // 中分黄色
    return 'rgba(245, 108, 108, 0.15)'; // 低分红色
}

const fetchReportData = async () => {
  loading.value = true;
  errorMessage.value = null;
  try{
    const response = await getEvaluationTaskDetail(props.taskId);
    if (response.data?.code === 200) {
        reportData.value = response.data;
    } else {
        errorMessage.value = '获取评测报告失败';
    }
  }catch(error){
    errorMessage.value = '获取评测报告时发生错误';
    console.error('获取评测报告错误:', error);
  }
}

onMounted(() => {
    fetchReportData();
})
</script>

<style scoped>
.report-detail {
  padding: 30px;
  background: transparent;
  min-height: 100vh;
}

.report-title {
  display: flex;
  align-items: center;
  font-size: 24px;
  color: #c9d1d9;
  margin-bottom: 20px;
}
.report-title .el-icon {
  margin-right: 10px;
  font-size: 28px;
  color: #409eff;
}

.meta-card {
  margin-bottom: 25px;
  background: #161b22;
  border: 1px solid #30363d;
}

:deep(.el-card__header) {
  border-bottom: 1px solid #30363d;
  color: #c9d1d9;
}

.summary-row {
  margin-bottom: 30px;
}

/* 统计卡片样式 */
.summary-card {
  text-align: center;
  border-radius: 8px;
  background: #161b22;
  border: 1px solid #30363d;
  transition: transform 0.3s, border-color 0.3s;
}

.summary-card:hover {
  transform: translateY(-3px);
  border-color: #58a6ff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.5);
}

.summary-value {
  font-size: 28px;
  font-weight: bold;
  color: #c9d1d9;
  margin-bottom: 5px;
}
.summary-label {
  font-size: 14px;
  color: #8b949e;
}
.score-value {
  color: #e6a23c; /* 强调得分 */
}

.summary-card :deep(.el-card__body) {
  padding: 20px;
  transition: background-color 0.3s;
}

/* 详细条目 */
.section-title {
  font-size: 18px;
  color: #c9d1d9;
  margin-bottom: 15px;
}

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

/* Pagination */
.pagination-container {
  margin-top: 20px;
  text-align: center;
  display: flex;
  justify-content: center;
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

/* Result Icons */
.result-icon {
  font-size: 18px;
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
  background-color: #161b22 !important;
  color: #8b949e !important;
}

:deep(.el-descriptions__content) {
  background-color: #0d1117 !important;
  color: #c9d1d9 !important;
}

:deep(.el-descriptions__cell) {
  border-color: #30363d !important;
}

:deep(.el-divider) {
  border-color: #30363d;
}
</style>