<template>
  <div class="report-detail">
    <div v-if="reportData && reportData.id" class="report-content" v-loading="loading">
      
      <h2 class="report-title">
        <el-icon><Document /></el-icon> 主观评测报告
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
            <div class="meta-value info">{{ reportData.method === 'subjective' ? '主观评测' : reportData.method }}</div>
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
      
      <el-divider class="meta-divider" /> 
      
      <el-row :gutter="20" class="summary-row">
        <el-col :span="12" :offset="6">
          <el-card 
            shadow="hover" 
            class="summary-card" 
            :style="{ backgroundColor: getScoreColor(reportData.score) }"
          >
            <div class="summary-value">{{ formatScore(reportData.score) }}</div>
            <div class="summary-label">整体平均分 (Average Score / 10)</div>
          </el-card>
        </el-col>
      </el-row>

      <h3 class="section-title">📝 评测条目详情 (第 {{ currentPage }}/{{ totalCount }} 条)</h3>
      
      <div v-if="currentItem">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="input-card" shadow="hover">
              <template #header>
                <span class="section-title">问题 (Question)</span>
              </template>
              <blockquote class="prompt-text">
                {{ currentItem.content }}
              </blockquote>
              <p class="meta-info">条目 ID: {{ currentItem.id }}</p>
            </el-card>
          </el-col>

          <el-col :span="12">
            <el-card class="model-output-card" shadow="hover">
              <template #header>
                <span class="section-title">模型输出 (Model Output)</span>
              </template>
              <div class="model-response">
                {{ currentItem.predicted_answer }} 
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-card class="rating-card" shadow="always">
          <template #header>
            <span class="section-title rating-title result-score-title">已提交评分</span>
          </template>
          
          <el-form :model="currentItem">
            <el-form-item class ="comprehensive-score-item">
              <div class="score-labels-low">
                  <span class="label-low">极差 (1)</span>
              </div>
              <el-radio-group
                v-model="currentItem.score" 
                class="round-rating-group"
                disabled >
                <el-radio-button
                  v-for="score in 10"
                  :key="score"
                  :label="score"
                  :value="score"
                >
                  {{ score }}
                </el-radio-button>
              </el-radio-group>
              <div class="score-labels-high">
                  <span class="label-high">优秀 (10)</span>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </div>
      <el-empty v-else description="条目数据加载失败或列表为空" />

      <div class="navigation-footer">
          <div class="page-navigation">
              <el-button @click="handlePrevious" :disabled="currentPage === 1">上一题</el-button>
          </div>

          <div class="pagination-controls">
              <el-pagination
                small
                layout="prev, pager, next"
                :total="totalCount"
                :page-size="1"
                :current-page="currentPage"
                :pager-count="11"
                @current-change="handlePageChange"
                class="custom-pager"
              />
              <div class="goto-input">
                  <el-input-number
                      v-model="gotoPageNum"
                      :min="1"
                      :step="1"
                      size="small"
                      controls-position="right"
                      style="width: 100px; margin-left: 15px;"
                      @change="handleGotoPage"
                  />
              </div>
          </div>

          <div class="page-navigation">
              <el-button 
                  type="primary" 
                  @click="handleNext" 
                  :disabled="currentPage === totalCount"
              >
                  下一题
              </el-button>
          </div>
        </div>
        
    </div>
    
    <el-empty v-else :description="errorMessage || '未找到评测报告'" />

  </div>
</template>

<script setup>
import { computed, ref, onMounted, defineProps } from 'vue'
import { Document, Tickets } from '@element-plus/icons-vue' // 引入 Tickets 图标
import { getEvaluationTaskDetail } from '../../api/tasks.js' // 假设的 API 路径

const currentPage = ref(1)
const gotoPageNum = ref(null);
const pageSize = 1 // 核心：设置为 1，实现单条目展示

const props = defineProps({
    taskId: {
        type: Number,
        required: true
    }
})

// ===================== 响应式数据定义 (继承自报告) =====================
const reportData = ref({
    id: null,
    method: '',
    status: '', 
    score: null, 
    data: [], // 包含所有条目的数组
});

const loading = ref(true); 
const errorMessage = ref(null); 

// ===================== 核心计算属性 =====================

const totalCount = computed(() => reportData.value.data.length);

const currentItem = computed(() => {
    if (!reportData.value || !Array.isArray(reportData.value.data) || totalCount.value === 0) {
        return null;
    }
    const index = currentPage.value - 1;
    // 返回当前页对应的条目数据
    return reportData.value.data[index] || null;
});


// ===================== 辅助函数 (适配主观报告) =====================

const formatScore = (rate) => {
  if (rate === undefined || rate === null) return 'N/A'
  return `${rate.toFixed(2)} / 10` 
}

// 根据平均分返回背景颜色
const getScoreColor = (rate) => {
    if (rate >= 9) return '#E8F5E9'; 
    if (rate >= 7) return '#FFFDE7'; 
    return '#FFEBEE'; 
}

// 根据单个评分返回 Tag 样式 (此处未使用，但保留)
const getScoreTagType = (score) => {
    if (score >= 9) return 'success';
    if (score >= 7) return 'warning';
    return 'danger';
}

// ===================== 导航逻辑 (处理分页切换) =====================

const handlePageChange = (page) => {
    if (page >= 1 && page <= totalCount.value) {
        currentPage.value = page;
    }
};

const handlePrevious = () => {
    if (currentPage.value > 1) {
        currentPage.value -= 1;
    }
};

const handleNext = () => {
    if (currentPage.value < totalCount.value) {
        currentPage.value += 1;
    }
};

const handleGotoPage = (value) => {
    
    if (value === null || value < 1 || value > totalCount.value) {
        ElMessage.warning(`不存在该页面，请输入 1 到 ${totalCount.value} 之间的页码。`);
        setTimeout(() => {
            gotoPageNum.value = currentPage.value;
        }, 50); 
        return;
    }

    currentPage.value = value;
};


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
        // 确保在数据加载完成后，如果列表不为空，则设置当前页为 1
        if (reportData.value.data.length > 0) {
            currentPage.value = 1; 
        }
    } else {
        errorMessage.value = '获取评测报告失败：返回数据为空或无效。';
        reportData.value.id = null; 
    }

  }catch(error){
    errorMessage.value = '获取主观评测报告时发生错误';
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
/* ======================== 报告容器和背景 (保持不变) ======================== */
.report-detail {
  padding: 40px; 
  background-color: #f7f9fc; 
  min-height: 100vh;
}

/* ======================== 标题和分割线 (保持不变) ======================== */
.report-title {
  display: flex;
  align-items: center;
  font-size: 32px; 
  font-weight: 600; 
  color: #2c3e50; 
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

/* ======================== 基础信息卡片 (保持不变) ======================== */
.meta-row {
    margin-bottom: 20px;
}
.meta-item-card {
    text-align: center;
    border-radius: 10px;
    height: 120px; 
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: all 0.3s ease;
    cursor: default;
    background-color: #ffffff;
    border: 1px solid #e0e6ed;
}
.meta-item-card:hover {
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
    border-color: var(--el-color-primary-light-3);
}

.meta-label {
    font-size: 14px;
    color: #8c939d;
    margin-bottom: 8px;
    font-weight: 500;
}

.meta-value {
    font-size: 28px; 
    font-weight: bold;
    line-height: 1.2;
}

.meta-value.primary {
    color: var(--el-color-primary); 
}

.meta-value.info {
    color: var(--el-color-info); 
}

.meta-value.status {
    height: 35px; 
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
  color: #1a2a3a;
  margin-bottom: 8px;
  line-height: 1;
}
.summary-label {
  font-size: 16px;
  color: #5f748c;
}

/* ======================== 单条目卡片样式 (借鉴自 SubjectiveEval.vue) ======================== */
.section-title {
  font-size: 22px;
  font-weight: 600;
  color: #34495e;
  margin-bottom: 20px;
  padding-left: 5px;
}
.input-card, .model-output-card {
  height: 400px; /* 固定高度，与评测页一致 */
  overflow-y: auto; 
  margin-bottom: 20px;
}

/* Prompt 样式 */
.prompt-text {
  padding: 10px;
  border-left: 5px solid var(--el-color-info-light-5);
  margin: 10px 0;
  background-color: var(--el-color-info-light-9);
  color: #606266;
  font-style: italic;
  min-height: 100px;
}
.meta-info {
    font-size: 12px;
    color: var(--el-color-info);
}

/* Model Output 样式 */
.model-response {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #303133;
}

/* 评分区域样式 (借鉴自 SubjectiveEval.vue) */
.rating-card {
  margin-top: 20px;
}
.rating-title {
    color: var(--el-color-danger);
}
/* 结果页的评分标题使用主色调 */
.result-score-title {
    color: var(--el-color-primary); 
}

.comprehensive-score-item :deep(.el-form-item__content) {
    display: flex;
    justify-content: center; 
    align-items: center; 
    gap: 10px;
}
.score-labels-low{
    display: flex;
    justify-content: space-between;
    font-size: 18px;
    color: var(--el-color-danger);
    font-weight: bold;
}

.score-labels-high{
    display: flex;
    justify-content: space-between;
    font-size: 18px;
    color: var(--el-color-success);
    font-weight: bold;
}
.round-rating-group {
    display: flex;
    flex-wrap: nowrap;
    max-width: 600px; 
    border: none !important; 
    box-shadow: none !important;
}
.round-rating-group :deep(.el-radio-button) {
    margin-left: 6px;
    margin-right: 6px; 
    border: none !important;
}
.round-rating-group :deep(.el-radio-button__inner) {
    width: 42px;
    height: 42px;
    line-height: 42px; 
    padding: 0; 
    font-size: 16px;
    font-weight: bold;
    border-radius: 50% !important;
    border: 2px solid var(--el-color-info-light-7);
    background-color: var(--el-color-white);
}
/* 禁用状态下已选中按钮的样式 (结果页保持选中效果) */
.round-rating-group :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
    background-color: var(--el-color-primary) !important;
    color: var(--el-color-white) !important;
    border-color: var(--el-color-primary) !important;
    transform: scale(1.05);
}

/* --- 底部导航栏样式 (来自 SubjectiveEval.vue) --- */
.navigation-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 25px;
  padding: 15px 0;
  border-top: 1px solid #ebeef5;
}
.page-navigation {
    width: 120px;
    text-align: center;
}

.pagination-controls {
    display: flex;
    align-items: center;
    gap: 15px;
}
.custom-pager :deep(.el-pager li) {
    min-width: 30px;
    height: 30px;
    line-height: 30px;
    font-size: 14px;
}

/* 移除原表格的样式，只保留必要的 */
.text-ellipsis {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    max-width: 100%;
}
</style>