<template>
  <div class="evaluation-page">
    <div v-if="reportData && reportData.id" v-loading="loading">
      <el-card class="eval-card" shadow="never">
        <template #header>
          <div class="card-header">
            <h2 class="title">
               <el-icon style="vertical-align: middle; margin-right: 8px;"><Histogram /></el-icon>
               对抗评测结果查看
            </h2>
            <el-tag type="warning" size="large">任务名称: {{ reportData.id }}</el-tag>
          </div>
        </template>

        <el-row :gutter="20" class="meta-row">
          <el-col :span="8"> <el-card shadow="hover" class="meta-item-card">
              <div class="meta-label">任务状态</div>
              <div class="meta-value status value-content">
                <el-tag :type="reportData.status === 'completed' ? 'success' : 'info'" effect="dark">
                  {{ reportData.status }}
                </el-tag>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="meta-item-card">
            <div class="meta-label">评测方法</div>
            <div class="meta-value value-wrapper value-content">
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
          <el-col :span="8"> <el-card shadow="hover" class="meta-item-card">
              <div class="meta-label">评测用时</div>
              <div class="meta-value value-content">{{ formatTimeUsed(reportData.time_used) }}</div>
            </el-card>
          </el-col>
        </el-row>

        <div v-if="reportData.description" class="description-container">
          <p class="description-text"><strong>任务描述：</strong>{{ reportData.description }}</p>
        </div>

        <el-row :gutter="20" class="summary-row" >
          <el-col :span="24">
            <el-card shadow="hover" class="accuracy-card">
              <div class="accuracy-content">
                <div class="accuracy-info">
                  <span class="accuracy-label">模型 A 胜率 (Win Rate)</span>
                  <span class="accuracy-value">{{ (reportData.accuracy * 100).toFixed(2) }}%</span>
                </div>
                <el-progress 
                  :percentage="parseFloat((reportData.accuracy * 100).toFixed(2))" 
                  :stroke-width="18" 
                  :status="reportData.accuracy >= 0.5 ? 'success' : 'warning'"
                  striped 
                  striped-flow 
                />
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-divider />

        <div v-if="currentItem">
          <el-card class="prompt-card" shadow="hover">
            <template #header>
              <span class="section-title prompt-title">问题 (Question)</span>
            </template>
            <blockquote class="prompt-text">
              {{ currentItem.content }}
            </blockquote>

            
            <div v-if="currentItem.content && currentItem.image_data" class="image-box">
              <el-image 
                :src="'data:image/png;base64,' + currentItem.image_data" 
                :preview-src-list="['data:image/png;base64,' + currentItem.image_data]"
                fit="contain"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                    <span>图片加载失败</span>
                  </div>
                </template>
              </el-image>
              <div class="image-tip">点击图片查看高清大图</div>
            </div>
          </el-card>

          <el-row :gutter="20" class="model-comparison">
            <el-col :span="12">
              <el-card class="model-output-card" shadow="hover">
                <template #header>
                  <span class="section-title model-a-title">
                    模型A：{{ reportData.myModel_name || '模型 A' }}
                  </span>
                </template>
                <div class="model-response">
                  <div class="markdown-body" v-html="renderedResponse1"></div>
                </div>
              </el-card>
            </el-col>

            <el-col :span="12">
              <el-card class="model-output-card" shadow="hover">
                <template #header>
                  <span class="section-title model-b-title">
                    模型B：{{ reportData.myModel_2_name || '模型 B' }}
                  </span>
                </template>
                <div class="model-response">
                  <div class="markdown-body" v-html="renderedResponse2"></div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-card class="rating-card" shadow="always">
            <template #header>
              <span class="section-title judgement-title">已提交偏好结果</span>
            </template>
            
            <div class="preference-display">
              <el-radio-group v-model="currentItem.preference" size="large" disabled>
                <el-radio-button label="left">左边更好</el-radio-button>
                <el-radio-button label="tie">平局</el-radio-button>
                <el-radio-button label="right">右边更好</el-radio-button>
              </el-radio-group>
            </div>
          </el-card>
        </div>
        <el-empty v-else description="暂无条目数据" />

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
            />
            <el-input-number
              v-model="gotoPageNum"
              :min="1"
              :max="totalCount"
              size="small"
              controls-position="right"
              style="width: 100px; margin-left: 15px;"
              @change="handlePageChange"
            />
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
      </el-card>
    </div>

    <el-empty v-else :description="errorMessage || '未找到评测报告'" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { Histogram, User, Service, Picture } from '@element-plus/icons-vue';
import { getEvaluationTaskDetail } from '../../api/tasks.js';
import { getAllModels } from '../../api/models.js';
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import { ElMessage } from 'element-plus';

const props = defineProps({
  taskId: {
    type: [String, Number],
    required: true
  }
});

// 响应式状态
const loading = ref(true);
const errorMessage = ref(null);
const currentPage = ref(1);
const gotoPageNum = ref(1);
const allModels = ref([]);

const reportData = ref({
  id: null,
  name:null,
  description: null,
  time_used: null,
  myModel_name: null,
  myModel_2_name: null,
  judge_model: null,
  accuracy: null,
  status: '',
  data: [] // 后端响应体包含 predicted_answer, predicted_answer2, preference
});

// 计算属性
const totalCount = computed(() => reportData.value.data?.length || 0);

const judgeModelName = computed(() => {
    if (reportData.value.judge_type === 'model' && reportData.value.judge_model) {
        const model = allModels.value.find(m => m.id === reportData.value.judge_model);
        return model ? model.name : `模型 ID: ${reportData.value.judge_model}`;
    }
    return '';
});

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

const currentItem = computed(() => {
  if (totalCount.value === 0) return null;
  return reportData.value.data[currentPage.value - 1];
});

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

const renderedResponse1 = computed(() => {
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

const renderedResponse2 = computed(() => {
  if (currentItem.value && currentItem.value.predicted_answer_2) {
    let content = currentItem.value.predicted_answer_2;
    content = content.replace(/\*\*\s+/g, '**').replace(/\s+\*\*/g, '**');
    content = content.replace(/\*\*\s+：/g, '**：').replace(/\*\*\s+:/g, '**:');
    let htmlContent = md.render(currentItem.value.predicted_answer_2);
    htmlContent = htmlContent.replace(/>\s+</g, '><');
    return htmlContent;
  }
  return '';
});

// 数据获取
const fetchReportData = async () => {
  loading.value = true;
  errorMessage.value = null;
  try {
    const [response, modelsRes] = await Promise.all([
        getEvaluationTaskDetail(props.taskId),
        getAllModels() 
    ]);

    allModels.value = modelsRes.data || [];
    if (response.data && response.data.id) {
      reportData.value = response.data;
      if (reportData.value.status !== 'completed') {
        errorMessage.value = `任务状态：${reportData.value.status}，请稍后再试。`;
      }
    } else {
      errorMessage.value = '获取数据无效';
    }
  } catch (error) {
    errorMessage.value = '请求报告详情失败';
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 分页逻辑
const handlePageChange = (page) => {
  if (page >= 1 && page <= totalCount.value) {
    currentPage.value = page;
    gotoPageNum.value = page;
  }
};

const handlePrevious = () => {
  if (currentPage.value > 1) handlePageChange(currentPage.value - 1);
};

const handleNext = () => {
  if (currentPage.value < totalCount.value) handlePageChange(currentPage.value + 1);
};

onMounted(() => {
  fetchReportData();
});
</script>

<style scoped>
/* 继承并微调 SubjectResult 的样式 */
.evaluation-page {
  padding: 40px;
  background-color: var(--bg-body);
  min-height: 100vh;
}

.eval-card {
  max-width: 1300px;
  margin: 0 auto;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 26px;
  color: var(--text-primary);
  margin: 0;
}

/* 基础信息卡片样式 */
.meta-row {
  margin-bottom: 20px;
}
.meta-item-card {
  height: 110px; /* 稍微增加高度以预留充足空间 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-radius: 10px;
  background-color: var(--bg-secondary);
}

/* 重点：固定 Label 高度，确保三个卡片的标题在同一水平线 */
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
.model-value {
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
.meta-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}
.meta-value {
  font-size: 20px;
  font-weight: bold;
}

.description-container {
  background: var(--bg-secondary);
  padding: 12px 20px;
  border-radius: 8px;
  border-left: 4px solid var(--el-color-primary-light-5);
  margin-bottom: 30px;
  margin-top: 10px; /* 适当增加间距 */
}

.description-text {
  margin: 0;
  font-size: 14px;
  color: var(--text-regular);
  /* 移除原有的 ellipsis 限制，让其完整显示 */
  white-space: normal; 
  overflow: visible;
  text-overflow: clip;
}

.summary-row {
  margin-top: 10px;
  margin-bottom: 25px;
}

.accuracy-card {
  background: linear-gradient(135deg, var(--el-color-primary-light-9) 0%, var(--bg-secondary) 100%);
  border: 1px solid var(--el-color-primary-light-7);
  border-radius: 12px;
}

.accuracy-content {
  padding: 10px 20px;
}

.accuracy-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 15px;
}

.accuracy-label {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-regular);
}

.accuracy-value {
  font-size: 36px;
  font-weight: 800;
  color: var(--el-color-primary);
  line-height: 1;
}

/* 进度条文字微调 */
:deep(.el-progress__text) {
  font-weight: bold;
  font-size: 14px !important;
}

/* 问题区域 */
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}
.prompt-card {
  margin-bottom: 20px;
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}
.prompt-text {
  padding: 15px;
  border-left: 5px solid #409eff;
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
  font-style: italic;
  margin: 0;
}

/* 模型对比区域 */
.model-comparison {
  margin-bottom: 20px;
}
.model-output-card {
  height: 450px;
  overflow-y: auto;
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}
.model-a-title { color: #67c23a; }
.model-b-title { color: #e6a23c; }
.model-response {
  white-space: pre-wrap;
  line-height: 1.6;
  color: var(--text-primary);
}

/* 评分/偏好展示 */
.rating-card {
  text-align: center;
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}
.judgement-title {
  color: #f56c6c;
}
.preference-display {
  padding: 20px 0;
}

/* 禁用状态下选中的 Radio 颜色 (重点：确保可见度) */
:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #67c23a !important;
  color: white !important;
  border-color: #67c23a !important;
  opacity: 1 !important;
}

:deep(.el-radio-button__inner) {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--border-color);
}


/* 图片容器样式 */
.image-box {
  /* 与上方文本容器留下 20px 的间隙 */
  margin-top: 20px; 
  
  /* 视觉上的修饰：边框、圆角和背景 */
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background-color: #fcfcfc;
  
  /* 居中显示 */
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 图片本身的样式 */
.image-box .el-image {
  width: 50%;
  max-height: 450px; /* 限制高度，防止长图撑破屏幕 */
  border-radius: 4px;
  cursor: zoom-in; /* 提示用户可以点击放大 */
  transition: all 0.3s;
}

/* 鼠标悬停微调 */
.image-box .el-image:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.image-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

/* 底部导航 */
.navigation-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.page-navigation {
  width: 150px;
}

.pagination-controls {
  display: flex;
  align-items: center;
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