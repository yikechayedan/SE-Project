<template>
  <div class="report-detail">
    <div v-if="reportData && reportData.id" class="report-content" v-loading="loading">
      
      <h2 class="report-title">
        <el-icon><Document /></el-icon> 主观评测报告
      </h2>

      <div class="report-subtitle-bar">
        <el-space spacer="|">
          <span class="sub-item">被评测模型：<strong>{{ reportData.myModel_name }}</strong></span>
          <span class="sub-item">数据集：<strong>{{ reportData.dataset_name }}</strong></span>
          <span class="sub-item">创建者：{{ reportData.creator_username }}</span>
        </el-space>
      </div>

      <el-divider class="title-divider" />

      <h3 class="section-title">📚 基础信息</h3>
      <el-row :gutter="20" class="meta-row">
        <el-col :span="6">
          <el-card shadow="hover" class="meta-item-card">
            <div class="meta-label">评测名称</div>
            <div class="meta-value primary small-text">{{ reportData.name }}</div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card shadow="hover" class="meta-item-card">
            <div class="meta-label">裁判类型</div>
            <div class="meta-value info">
                <el-tag :type="reportData.judge_type === 'human' ? 'warning' : 'primary'" size="small" class="judge-tag">
                    <el-icon><User v-if="reportData.judge_type === 'human'" /><service v-else /></el-icon>
                    {{ reportData.judge_type === 'human' ? '人类裁判' : '模型裁判' }}
                </el-tag>
                <el-tooltip
                    v-if="reportData.judge_type === 'model'"
                    class="box-item"
                    effect="dark"
                    :content="judgeModelName"
                    placement="top"
                  >
                    <span class="judge-model-inline-name">
                      {{ judgeModelName }}
                    </span>
                  </el-tooltip>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card shadow="hover" class="meta-item-card">
            <div class="meta-label">运行耗时</div>
            <div class="meta-value info time-text">{{ formatTimeUsed(reportData.time_used) }}</div>
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

      <div v-if="reportData.description" class="description-container">
        <p class="description-text"><strong>评测描述：</strong>{{ reportData.description }}</p>
      </div>
      
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
                <div class="markdown-body" v-html="renderedResponse"></div>
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
import { Document, Tickets, User, Service } from '@element-plus/icons-vue' // 引入 Tickets 图标
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import { getEvaluationTaskDetail } from '@/api/tasks.js' // 假设的 API 路径
import { getAllModels } from '@/api/models.js' 

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
const allModels = ref([])

const reportData = ref({
    id: null,
    method: '',
    status: '', 
    score: null, 
    data: [],
    description: '',
    time_used: '',
    myModel_name: '',
    dataset_name: '',
    creator_username: '',
    judge_type: '',
    judge_model: null,
});

const judgeModelName = computed(() => {
    if (reportData.value.judge_type === 'model' && reportData.value.judge_model) {
        const model = allModels.value.find(m => m.id === reportData.value.judge_model);
        return model ? model.name : `模型 ID: ${reportData.value.judge_model}`;
    }
    return '';
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

const md = new MarkdownIt({
  html: true,         // 允许 HTML 标签
  linkify: true,      // 自动转换 URL
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
               hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
               '</code></pre>';
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
  }
});

const renderedResponse = computed(() => {
  if (currentItem.value && currentItem.value.predicted_answer) {
    let content = currentItem.value.predicted_answer;
    content = content.replace(/\*\*\s+/g, '**').replace(/\s+\*\*/g, '**');
    content = content.replace(/\*\*\s+：/g, '**：').replace(/\*\*\s+:/g, '**:');
    let htmlContent = md.render(currentItem.value.predicted_answer);
    htmlContent = htmlContent.replace(/>\s+</g, '><');
    return htmlContent;
  }
  return '';
});

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
    const [response, modelsRes] = await Promise.all([
        getEvaluationTaskDetail(props.taskId),
        getAllModels() 
    ]);

    allModels.value = modelsRes.data || [];

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
  background-color: var(--bg-body); 
  min-height: 100vh;
}

/* ======================== 标题和分割线 (保持不变) ======================== */
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

/* ======================== 基础信息卡片 (保持不变) ======================== */
/* 顶部副标题栏 */
.report-subtitle-bar {
  margin-bottom: 15px;
  font-size: 14px;
  color: var(--text-secondary);
}
.sub-item strong {
  color: var(--el-color-primary);
  margin-left: 4px;
}

/* 裁判模型名称微调 */
.judge-model-name {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
  font-weight: normal;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 耗时字体 */
.time-text {
  font-size: 22px !important;
  font-family: 'Courier New', Courier, monospace;
}

.meta-label {
  font-size: 14px;
  color: var(--text-secondary);
  height: 20px;       /* 固定高度 */
  line-height: 20px;  /* 确保文字垂直居中 */
  margin-bottom: 12px;/* 统一间距 */
  text-align: center;
  width: 100%;
}

/* 重点：固定数据区域高度，确保下方内容不会推挤标题 */
.meta-value {
  display: flex;
  flex-direction: row;
  align-items: center;    /* 垂直方向居中对齐 */
  justify-content: center;/* 水平方向居中对齐 */
  height: 32px;           /* 固定高度，匹配 el-tag 的高度 */
  gap: 8px;               /* 元素间距 */
  width: 100%;
  font-size: 20px;
  font-weight: bold;
}

/* 模型名称微调 */
.judge-model-inline-name {
  font-size: 14px;
  color: var(--el-color-info);
  font-weight: normal;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px; /* 限制宽度防止撑开 */
}

/* 修正 el-tag 图标对齐 */
.judge-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

/* 描述容器 */
.description-container {
  background: var(--bg-secondary);
  padding: 12px 20px;
  border-radius: 8px;
  border-left: 4px solid var(--el-color-primary-light-5);
  margin-bottom: 30px;
}
.description-text {
  margin: 0;
  font-size: 14px;
  color: var(--text-regular);
}

/* 基础信息卡片高度适配 4 列 */
.meta-item-card {
  height: 110px;
}
.small-text {
  font-size: 20px !important;
}

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
  /* Fallback or let inline style override, but default border needed */
  border: 1px solid var(--border-color);
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
  color: #1a2a3a; /* Keeping high contrast dark color for light bg card, or update if card bg is dark */
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
  color: var(--text-primary);
  margin-bottom: 20px;
  padding-left: 5px;
}
.input-card, .model-output-card {
  height: 400px; /* 固定高度，与评测页一致 */
  overflow-y: auto; 
  margin-bottom: 20px;
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}

/* Prompt 样式 */
.prompt-text {
  padding: 10px;
  border-left: 5px solid var(--el-color-info-light-5);
  margin: 10px 0;
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
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
  color: var(--text-primary);
}

/* 评分区域样式 (借鉴自 SubjectiveEval.vue) */
.rating-card {
  margin-top: 20px;
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
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
    border: 2px solid var(--border-color);
    background-color: var(--bg-tertiary);
    color: var(--text-primary);
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
  border-top: 1px solid var(--border-color);
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
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}
.custom-pager :deep(.el-pager li.is-active) {
    background-color: var(--el-color-primary) !important;
    color: #ffffff !important;
}

/* 移除原表格的样式，只保留必要的 */
.text-ellipsis {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    max-width: 100%;
}

/* 容器基础设置 */
.markdown-body {
  font-size: 18px;            /* 调大字号 */
  line-height: 1.75;          /* 黄金行高 */
  color: #2c3e50;             /* 深灰色文字，比纯黑更柔和 */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  word-wrap: break-word;
  user-select: text !important; /* 核心：确保全文可选 */
  overflow-wrap: break-word; /* 确保长单词能换行，不至于撑破容器 */
}

/* 表格容器：这是最容易超出宽度的地方 */
.markdown-body :deep(table) {
  display: block;
  width: 100% !important;
  overflow-x: auto;
  border-spacing: 0;
  border-collapse: collapse;
  word-break: normal;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

/* 单元格边框与内边距 */
.markdown-body :deep(table th),
.markdown-body :deep(table td) {
  /* 1. 设置最小宽度，防止内容被挤压成一竖排 */
  min-width: 120px; 
  
  /* 2. 允许内容折行（如果你不希望它一直横向延伸） */
  /* 或者保持 white-space: nowrap; 如果你想要整行显示并触发滚动条 */
  white-space: normal; 
  
  word-break: break-all;
  padding: 10px 15px;
  line-height: 1.5;
}

/* 解决加粗文字与文本间隙的同时，允许其在极长情况下不撑破布局 */
.markdown-body :deep(strong) {
  display: inline; /* 改回 inline 配合 word-break */
  white-space: normal; 
}

/* 1. 段落间距控制：这是消除“大空行”的关键 */
.markdown-body :deep(p) {
  margin-top: 0;
  margin-bottom: 12px;        /* 限制段落间距 */
}

/* 2. 列表样式：模拟 AI 的缩进感并确保标号可选 */
.markdown-body :deep(ol), 
.markdown-body :deep(ul) {
  padding-left: 2em;
  margin-top: 4px;
  margin-bottom: 12px;
}

.markdown-body :deep(li) {
  margin-bottom: 6px;         /* 列表项之间的微小间距 */
  list-style-position: outside; 
}

/* 3. 解决标号选中问题 */
.markdown-body :deep(li::marker) {
  font-weight: 600;
  color: #409eff;             /* 标号使用主题色，视觉更清晰 */
  user-select: text;          /* 允许选中标号 */
}

.markdown-body :deep(li) {
  white-space: normal !important; /* 列表项通常不需要保留原始换行 */
}

.markdown-body :deep(li p) {
  display: inline; /* 让 p 标签不作为块级撑开，紧随标号 */
  white-space: normal;
}

.markdown-body :deep(hr) {
  height: 1px;
  background-color: #e1e4e8;
  border: none;
  margin: 20px 0;
}

.markdown-body :deep(pre) {
    display: block;          /* 确保是块级元素 */
    width: 100%;             /* 占据全宽 */
    overflow-x: auto;        /* 关键：宽度不足时显示横向滚动条 */
    overflow-y: hidden;      /* 隐藏纵向滚动条 */
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    
    /* 强制代码不换行，这样才能触发横向滚动条 */
    white-space: pre;        
    word-break: normal;
    word-wrap: normal;
}

/* 针对代码块内部的 code 标签 */
.markdown-body :deep(pre code) {
    display: inline;         /* 保持内联以便在 pre 中横向延伸 */
    max-width: none;
    padding: 0;
    margin: 0;
    white-space: pre;        /* 再次确保不换行 */
}

.markdown-body {
  white-space: pre-wrap;      /* 保留原始缩进（如 \t），但允许自动换行 */
}
</style>