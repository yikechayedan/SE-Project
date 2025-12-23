<template>
  <div class="report-detail">
    <div v-if="reportData && reportData.id" class="report-content">
      
      <h2 class="report-title">
        <el-icon><Document /></el-icon> 评测报告
      </h2>

      <div class="report-subtitle">
        <el-tag v-if="reportData.myModel_name" effect="plain" round type="primary">模型：{{ reportData.myModel_name }}</el-tag>
        <el-tag v-if="reportData.dataset_name" effect="plain" round type="success">数据集：{{ reportData.dataset_name }}</el-tag>
        <span class="creator-info">由 <b>{{ reportData.creator_username }}</b> 创建</span>
      </div>

      <el-divider class="title-divider" />

      <h3 class="section-title">📚 基础信息</h3>
      <el-row :gutter="20" class="meta-row">
        <el-col :span="6">
          <el-card shadow="hover" class="meta-item-card">
            <div class="meta-label">评测名称</div>
            <div class="meta-value primary small">{{ reportData.name }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="meta-item-card">
            <div class="meta-label">评测方法</div>
            <div class="meta-value info">{{ reportData.method == 'objective' ? '客观评测' : reportData.method }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="meta-item-card">
            <div class="meta-label">任务耗时</div>
            <div class="meta-value info">{{ formatTimeUsed(reportData.time_used) }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="meta-item-card">
            <div class="meta-label">任务状态</div>
            <div class="meta-value status">
              <el-tag :type="reportData.status === 'completed' ? 'success' : 'info'" size="large" effect="dark">{{ reportData.status }}</el-tag>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <div v-if="reportData.description" class="description-box">
        <span class="desc-label">任务描述：</span>
        <span class="desc-content">{{ reportData.description }}</span>
      </div>
      
      <el-divider class="meta-divider" /> <el-row :gutter="20" class="summary-row">
        <el-col :span="12" :offset="6">
          <el-card shadow="hover" class="summary-card" :style="{ backgroundColor: getAccuracyColor(reportData.accuracy) }">
            <div class="summary-value">{{ formatAccuracy(reportData.accuracy) }}</div>
            <div class="summary-label">整体正确率 (Accuracy)</div>
          </el-card>
        </el-col>
      </el-row>

      <h3 class="section-title">📊 详细评测条目</h3>

      <div class="filter-container">
        <el-radio-group v-model="filterStatus" size="default">
          <el-radio-button label="all">全部题目</el-radio-button>
          <el-radio-button label="wrong">只看错题</el-radio-button>
        </el-radio-group>
      </div>
      
      <el-table :data="paginatedItems" border stripe class="detail-table">
        <el-table-column prop="id" label="条目 ID" width="100" />
        <el-table-column prop="content" label="题目/条目名称">
          <template #default="scope">
            <div class="question-text">{{ parseContent(scope.row.content).question }}</div>
            
            <div class="options-container">
              <div 
                v-for="(optText, optKey) in parseContent(scope.row.content).options" 
                :key="optKey"
                class="option-item"
                :class="{ 
                  'is-correct-option': optKey === scope.row.correct_answer,
                  'is-wrong-prediction': scope.row.is_correct !== 1 && optKey === (scope.row.predicted_answer ? scope.row.predicted_answer.trim().toUpperCase() : '')
                }"
              >
                <span class="option-key">{{ optKey }}.</span>
                <span class="option-val">{{ optText }}</span>
                <el-tag 
                  v-if="optKey === scope.row.correct_answer" 
                  size="small" 
                  type="success" 
                  effect="dark" 
                  class="status-tag">
                  正确答案
                </el-tag>
                <el-tag 
                  v-if="scope.row.is_correct !== 1 && optKey === (scope.row.predicted_answer ? scope.row.predicted_answer.trim().toUpperCase() : '')" 
                  size="small" 
                  type="danger" 
                  effect="plain" 
                  class="status-tag">
                  模型选择
                </el-tag>
              </div>
            </div>

            <!-- 【优化】只有当模型回答清洗后仍匹配不到选项时，才显示原始回答框 -->
            <div v-if="scope.row.predicted_answer && !parseContent(scope.row.content).options[scope.row.predicted_answer.trim().toUpperCase()]" class="raw-prediction-box">
              <span class="raw-label">模型原始回答：</span>
              <el-tag type="warning" size="small">{{ scope.row.predicted_answer.trim() }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="判定" width="100" align="center">
          <template #default="scope">
            <el-icon v-if="scope.row.is_correct === 1" class="result-icon correct-icon"><Check /></el-icon>
            <el-icon v-else-if="scope.row.is_correct === 0" class="result-icon incorrect-icon"><Close /></el-icon>
            <el-icon v-else class="result-icon unknown-icon" style="color: #909399;"><Minus /></el-icon>
          </template>
        </el-table-column>
      </el-table>

      <div class="navigation-footer">
        <div class="page-navigation">
          <el-button 
            type="primary" 
            plain 
            @click="handlePrevious" 
            :disabled="currentPage === 1"
          >
            <el-icon><ArrowLeft /></el-icon> 上一题
          </el-button>
        </div>

        <div class="pagination-controls">
          <el-pagination
            background
            layout="prev, pager, next"
            :total="filteredItems.length" 
            :page-size="pageSize"
            v-model:current-page="currentPage"
            class="custom-pager"
          />
          
          <div class="goto-input">
            <span class="goto-label">跳转至</span>
            <el-input-number
              v-model="currentPage"
              :min="1"
              :max="Math.ceil(filteredItems.length / pageSize) || 1"
              size="small"
              controls-position="right"
              @change="scrollToTop"
              style="width: 90px;"
            />
            <span class="goto-unit">页</span>
          </div>
        </div>
        
        <div class="page-navigation">
          <el-button 
            type="primary" 
            plain 
            @click="handleNext" 
            :disabled="currentPage >= Math.ceil(filteredItems.length / pageSize)"
          >
            下一题 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
    
    <el-empty v-else :description="errorMessage || '未找到评测报告'" />

  </div>
</template>

<script setup>
import { computed, ref, onMounted, defineProps } from 'vue'
import { Document, Check, Close, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { getEvaluationTaskDetail } from '@/api/tasks.js'

const currentPage = ref(1)
const pageSize = 10
const filterStatus = ref('all')

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
    description: '',
    time_used: 0,
    myModel_name: '',
    dataset_name: '',
    creator_username: ''
});

const loading = ref(true); 
const errorMessage = ref(null); 

// 获取根据筛选条件过滤后的全量数据
const filteredItems = computed(() => {
  if (!reportData.value || !Array.isArray(reportData.value.data)) return [];
  
  let filtered = reportData.value.data;
  if (filterStatus.value === 'wrong') {
    // 【修复】包括 0 和 null (兼容旧数据)
    filtered = reportData.value.data.filter(item => item.is_correct !== 1);
  }
  return filtered;
});

// 基于过滤后的数据进行分页截取
const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  const end = currentPage.value * pageSize;
  return filteredItems.value.slice(start, end);
});

import { watch } from 'vue';
watch(filterStatus, () => {
  currentPage.value = 1;
});

const parseContent = (fullText) => {
  if (!fullText) return { question: '', options: {} };

  // 匹配选项的正则表达式，假设格式为 A. xxx B. xxx ...
  const optionLetters = ['A', 'B', 'C', 'D'];
  let question = fullText;
  let options = {};

  // 寻找第一个选项出现的位置来截取问题
  const firstOptionIndex = fullText.search(/[A-D]\.\s/);
  
  if (firstOptionIndex !== -1) {
    question = fullText.substring(0, firstOptionIndex).trim();
    const optionsPart = fullText.substring(firstOptionIndex);

    optionLetters.forEach((letter, index) => {
      const currentMarker = `${letter}.`;
      const nextMarker = `${optionLetters[index + 1]}.`;
      
      const start = optionsPart.indexOf(currentMarker);
      if (start !== -1) {
        const end = nextMarker !== 'undefined.' ? optionsPart.indexOf(nextMarker) : optionsPart.length;
        
        // 提取选项内容并去掉开头的 "A." 部分
        let optContent = end !== -1 
          ? optionsPart.substring(start, end) 
          : optionsPart.substring(start);
          
        options[letter] = optContent.replace(`${letter}.`, '').trim();
      }
    });
  }

  return { question, options };
};

// ===================== 辅助函数 (保持不变) =====================
const formatTimeUsed = (timeStr) => {
  if (!timeStr) return '00:00:00';
  
  if (typeof timeStr === 'string' && timeStr.includes('.')) {
    return timeStr.split('.')[0];
  }
  
  // 方式 2：如果后端偶尔返回的是秒数（数字），则需要另一种逻辑
  if (typeof timeStr === 'number') {
    const h = Math.floor(timeStr / 3600).toString().padStart(2, '0');
    const m = Math.floor((timeStr % 3600) / 60).toString().padStart(2, '0');
    const s = Math.floor(timeStr % 60).toString().padStart(2, '0');
    return `${h}:${m}:${s}`;
  }

  return timeStr; // 兜底返回原字符串
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

// ===================== 动作处理函数 =====================
// 上一题/页
const handlePrevious = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    scrollToTop();
  }
}

// 下一题/页
const handleNext = () => {
  const maxPage = Math.ceil(filteredItems.value.length / pageSize); // 使用 filteredItems
  if (currentPage.value < maxPage) {
    currentPage.value++;
    scrollToTop();
  }
}

// 辅助：跳转后滚动回表格顶部，提升体验
const scrollToTop = () => {
  const tableEl = document.querySelector('.detail-table');
  if (tableEl) {
    tableEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
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
/* 副标题样式 */
.report-subtitle {
  margin-top: -10px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.creator-info {
  font-size: 14px;
  color: var(--text-secondary);
  margin-left: auto; /* 推到右侧 */
}

/* 缩小一点 ID 的字号以适应 4 列布局 */
.meta-value.small {
  font-size: 22px;
}

/* 描述区块样式 */
.description-box {
  margin: 0 0 30px 0;
  padding: 15px 20px;
  background-color: var(--bg-secondary);
  border-left: 4px solid var(--el-color-primary);
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.6;
}
.desc-label {
  font-weight: bold;
  color: var(--text-primary);
  margin-right: 8px;
}
.desc-content {
  color: var(--text-secondary);
}

/* 适配 4 列后的高度调整 */
.meta-item-card {
  height: 110px;
}

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

.filter-container {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-start;
}

.question-text {
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.option-item {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid transparent;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}

/* 正确选项高亮：浅绿 */
.is-correct-option {
  background-color: #f0f9eb !important;
  border-color: #c2e7b0 !important;
}
.is-correct-option .option-key { color: #67c23a; }

/* 错误预测高亮：浅红 */
.is-wrong-prediction {
  background-color: #fff1f0 !important;
  border-color: #ffa39e !important;
}
.is-wrong-prediction .option-key { color: #f5222d; }

.status-tag {
  margin-left: auto; /* 靠右对齐 */
  height: 20px;
}

.option-key {
  font-weight: bold;
  margin-right: 10px;
}

.raw-prediction-box {
  margin-top: 10px;
  padding: 8px 12px;
  background-color: var(--bg-secondary);
  border-radius: 6px;
  border: 1px dashed var(--warning-color);
  font-size: 13px;
  display: flex;
  align-items: center;
}
.raw-label {
  color: var(--text-secondary);
  margin-right: 8px;
}

.navigation-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 30px;
  padding: 20px 0;
  border-top: 1px solid var(--border-color);
  background-color: var(--bg-secondary); /* 给底部导航一个微弱的底色区分 */
  border-radius: 0 0 8px 8px;
}

.page-navigation {
  flex: 0 0 150px;
  display: flex;
  justify-content: center;
}

.pagination-controls {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}

.goto-input {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.goto-label {
  margin-right: 8px;
}

.goto-unit {
  margin-left: 8px;
}

/* 分页器样式优化 */
.custom-pager :deep(.el-pager li) {
  border-radius: 4px;
  font-weight: 600;
}

.custom-pager :deep(.el-pagination.is-background .btn-next), 
.custom-pager :deep(.el-pagination.is-background .btn-prev) {
  border-radius: 4px;
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