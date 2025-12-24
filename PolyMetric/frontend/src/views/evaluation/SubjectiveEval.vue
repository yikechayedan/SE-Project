<template>
  <div class="evaluation-page">
    <el-card class="eval-card" shadow="never" v-loading="loading">
      
      <template #header>
        <div class="card-header">
          <h2 class="title">主观评测</h2>
          <el-tag type="info">任务 ID: {{ taskId }}</el-tag>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="input-card" shadow="hover">
            <template #header>
              <span class="section-title">问题 (Question)</span>
            </template>
            <blockquote class="prompt-text" v-if="currentItem.itemID">
              {{ currentItem.item_content.input_query }}
            </blockquote>
            <div v-else class="content-placeholder">请等待问题加载...</div>
            <div v-if="currentItem.item_content && currentItem.item_content.image_data" class="image-box">
              <el-image 
                :src="'data:image/png;base64,' + currentItem.item_content.image_data" 
                :preview-src-list="['data:image/png;base64,' + currentItem.item_content.image_data]"
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
            <p class="meta-info">数据集 ID：{{ datasetId }} | 类型：开放式问答</p>
          </el-card>
        </el-col>

        <el-col :span="12">
            <el-card class="model-output-card" shadow="hover">
              <template #header>
                <span class="section-title">模型输出 (Model Output)</span>
              </template>
              <div class="model-response">
                <div v-if="!isPureImageResponse" class="markdown-body" v-html="renderedResponse"></div>
                <!-- 模型生成图片展示 -->
                <div v-if="currentItem && currentItem.predicted_image_data" class="gen-image-container">
                  <el-divider v-if="!isPureImageResponse" border-style="dashed">生成的图像结果</el-divider>
                  <el-image 
                    :src="formatBase64(currentItem.predicted_image_data)" 
                    :preview-src-list="[formatBase64(currentItem.predicted_image_data)]"
                    fit="contain"
                    class="responsive-gen-image"
                  />
                </div>
              </div>
            </el-card>

        </el-col>
      </el-row>
      
      <el-card class="rating-card" shadow="always">
        <template #header>
          <span class="section-title rating-title">请对模型回复进行评测 (主观评分)</span>
        </template>
        
        <el-form :model="form" v-if="currentItem.itemID">
          <el-form-item class="comprehensive-score-item">
            <div class="score-labels-low">
                <span class="label-low">极差 (1)</span>
            </div>
            <el-radio-group v-model="form.score" class="round-rating-group">
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
         <div v-else class="content-placeholder">请等待条目加载...</div>
      </el-card>
      
      <div class="navigation-footer">
        <div class="page-navigation">
            <el-button @click="handlePrevious" :disabled="!canGoPrevious">上一题</el-button>
        </div>
        
        <div class="page-navigation item-list-btn-wrapper">
            <el-button @click="drawerVisible = true" :disabled="loading">
                <el-icon><Tickets /></el-icon>
                <span>条目列表 ({{ totalCount }})</span>
            </el-button>
        </div>

        <div class="pagination-controls">
            <el-pagination
              small
              layout="prev, pager, next"
              :total="totalCount"
              :page-size="1"
              :current-page="currentPageIndex"
              :pager-count="11"
              @current-change="handlePageChange"
              class="custom-pager"
            />
            
            <div class="goto-input">
                <el-input-number
                    v-if="totalCount > 0"
                    v-model="gotoPageNum"
                    :min="1"
                    :max="totalCount"
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
                @click="handleSubmit" 
                :loading="submitting" 
                :disabled="form.score === null || loading"
            >
                {{ isLastItem ? '提交完成' : '提交并下一题' }}
            </el-button>
        </div>
      </div>

    </el-card>
    
    <el-drawer 
        v-model="drawerVisible" 
        title="评测条目列表" 
        direction="rtl" 
        size="350px"
    >
        <div class="item-id-grid">
            <el-button
                v-for="(id, index) in allItemIds"
                :key="id"
                :type="submissionStatus.get(id) ? 'primary' : 'info'"
                :plain="!submissionStatus.get(id)"
                :disabled="loading"
                :class="{ 'is-current': currentItemId === id }"
                @click="handleJumpToItemById(id)"
                class="item-id-button"
            >
                {{ index + 1 }}
            </el-button>
        </div>
        <div class="drawer-legend">
            <el-tag type="success" class="current-tag">当前条目 (绿色边框)</el-tag>
        </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter } from 'vue-router';
import { Tickets, Picture } from '@element-plus/icons-vue';
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import { getPendingItems, getItemDetail, submitSubjectiveScore } from '@/api/tasks.js';

// 接收父组件参数
const props = defineProps({
  taskId: { type: [String, Number], required: true },
  reviewerId: { type: [String, Number], required: true },
  modelId: { type: [String, Number], required: true },
  datasetId: { type: [String, Number], required: true }
});

// 状态管理
const loading = ref(false);
const submitting = ref(false);
const drawerVisible = ref(false);
const router = useRouter();

const totalCount = ref(0);
const allItemIds = ref([]); // 所有条目
const pendingItemIds = ref([]); // 待测条目
const submissionStatus = ref(new Map()); // 维护每个ID的完成状态 (ID -> Boolean)
const completedScoresMap = ref(new Map());

const currentItemId = ref(null);
const currentItem = ref({
  itemID: null,
  item_content: { input_query: '', myModel1_response: '' }
});

const form = reactive({ score: null });
const gotoPageNum = ref(1);

// --- 计算属性 ---

// 当前是第几页（基于 ID 在全量列表中的索引）
const currentPageIndex = computed(() => {
  // 增加对 allItemIds.value 的判断，防止数据未加载时报错
  if (!allItemIds.value || !Array.isArray(allItemIds.value)) {
    return 1;
  }
  const index = allItemIds.value.indexOf(currentItemId.value);
  return index !== -1 ? index + 1 : 1;
});

const canGoPrevious = computed(() => currentPageIndex.value > 1);

// 判断是否是最后一个待评分项
const isLastItem = computed(() => {
  // 增加安全判断：确保 pendingItemIds.value 存在且是数组
  if (!pendingItemIds.value || !Array.isArray(pendingItemIds.value)) {
    return false;
  }
  return pendingItemIds.value.length === 1 && pendingItemIds.value.includes(currentItemId.value);
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

// ===================== 辅助函数：格式化 Base64 =====================
const formatBase64 = (b64) => {
  if (!b64) return '';
  if (b64.startsWith('data:')) return b64;
  if (b64.startsWith('iVBORw')) return 'data:image/png;base64,' + b64;
  if (b64.startsWith('/9j/')) return 'data:image/jpeg;base64,' + b64;
  return 'data:image/jpeg;base64,' + b64;
};

const isPureImageResponse = computed(() => {
  if (!currentItem.value || !currentItem.value.predicted_answer) return false;
  return /^!\[.*?\]\s*\(.*\)$/.test(currentItem.value.predicted_answer.trim());
});

const renderedResponse = computed(() => {
  if (!currentItem.value || !currentItem.value.predicted_answer) return '';
  // 清除 Markdown 中的图片标签防止裂图
  const cleanContent = currentItem.value.predicted_answer.replace(/!\[.*?\]\s*\(.*\)/g, '');
  return md.render(cleanContent);
});


// --- 核心逻辑 ---

// 获取待测条目列表并初始化
const initData = async () => {
  loading.value = true;
  try {
    const res = await getPendingItems(props.taskId, props.reviewerId);
    
    allItemIds.value = res.data.all_item_ids || [];
    pendingItemIds.value = res.data.pending_item_ids || []; // 注意：此处根据你后端返回的 key 名对齐
    totalCount.value = res.data.total_count || 0;

    // 1. 清空旧状态
    submissionStatus.value.clear();
    completedScoresMap.value.clear();

    // 2. 处理已评测的数据
    if (res.data.completed_items) {
      res.data.completed_items.forEach(item => {
        submissionStatus.value.set(item.id, true);
        completedScoresMap.value.set(item.id, {
          score: item.score,
          preference: item.preference
        });
      });
    }

    // 3. 处理所有 ID 的完成状态（未在已评测列表中的即为 false）
    allItemIds.value.forEach(id => {
      if (!submissionStatus.value.has(id)) {
        submissionStatus.value.set(id, false);
      }
    });

    const targetId = pendingItemIds.value.length > 0 ? pendingItemIds.value[0] : allItemIds.value[0];
    if (targetId) await fetchDetail(targetId);
  } catch (error) {
    console.error('初始化数据失败:', error);
  } finally {
    loading.value = false;
  }
};

// 获取条目详情
const fetchDetail = async (id) => {
  loading.value = true;
  currentItemId.value = id;
  try {
    const res = await getItemDetail(props.taskId, id);
    
    // [Fix] 这里的后端响应是嵌套在 item_content 下的，需要手动拍平
    const content = res.data.item_content || {};
    currentItem.value = {
        ...res.data,
        content: content.input_query,
        image_data: content.image_data,
        predicted_answer: content.myModel1_response,
        predicted_image_data: content.predicted_image_data // 注入生图数据
    };

    // --- 分数回显核心逻辑 ---
    // 检查这个 ID 是否在已评测缓存中
    if (completedScoresMap.value.has(id)) {
      form.score = completedScoresMap.value.get(id).score;
    } else {
      form.score = null; // 如果没评测过，才重置为空
    }
    
    gotoPageNum.value = currentPageIndex.value;
  } catch (error) {
    ElMessage.error('加载条目详情失败');
  } finally {
    loading.value = false;
  }
};

// 提交逻辑
const handleSubmit = async () => {
  if (isLastItem.value) {
    ElMessageBox.confirm('这已经是最后一题了，提交后将结束评测任务。', '完成提示', {
      confirmButtonText: '提交并完成',
      cancelButtonText: '取消',
      type: 'success'
    }).then(() => executeSubmit(true));
  } else {
    executeSubmit(false);
  }
};

const executeSubmit = async (isFinal) => {
    submitting.value = true;
    try {
        const payload = {
        myModel: props.modelId,
        dataset: props.datasetId,
        reviewer: props.reviewerId,
        itemID: currentItemId.value,
        score: form.score,
        preference: null 
        };

        await submitSubjectiveScore(props.taskId, payload);
        ElMessage.success('提交成功');

        // 更新本地缓存，这样如果用户点“上一题”回来，就能看到刚才打的分数
        submissionStatus.value.set(currentItemId.value, true);
        completedScoresMap.value.set(currentItemId.value, { 
            score: form.score, 
            preference: null 
        });

        // 刷新列表数据（保持与后端同步）
        const res = await getPendingItems(props.taskId, props.reviewerId);
        pendingItemIds.value = res.data.pending_item_ids;

        if (isFinal) {
        router.push({ name: 'Evaluation' });
        } else {
        const nextPendingId = pendingItemIds.value.find(id => id !== currentItemId.value) || pendingItemIds.value[0];
        if (nextPendingId) {
            fetchDetail(nextPendingId);
        }
        }
    } catch (error) {
        ElMessage.error('提交分数失败');
    } finally {
        submitting.value = false;
    }
};

// --- UI 交互方法 ---

const handlePrevious = () => {
  const index = allItemIds.value.indexOf(currentItemId.value);
  if (index > 0) fetchDetail(allItemIds.value[index - 1]);
};

const handlePageChange = (page) => {
  // 1. 检查数组是否存在且有内容
  // 2. 检查计算出的索引是否在数组范围内
  if (allItemIds.value && allItemIds.value.length >= page) {
    const targetId = allItemIds.value[page - 1];
    if (targetId !== undefined) {
      fetchDetail(targetId);
    }
  } else {
    console.warn('正在尝试跳转到不存在的页码:', page);
  }
};

const handleGotoPage = (val) => {
  if (val) fetchDetail(allItemIds.value[val - 1]);
};

const handleJumpToItemById = (id) => {
  drawerVisible.value = false;
  fetchDetail(id);
};

onMounted(initData);
</script>

<style scoped>
/* 保持原有样式不变 */
.evaluation-page {
  padding: 20px;
  background-color: var(--bg-body);
  min-height: calc(100vh - 50px);
}

.eval-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-size: 24px;
  color: var(--text-primary);
}

/* --- 内容区域 --- */
.input-card, .model-output-card {
  height: 400px; 
  overflow-y: auto; 
  margin-bottom: 20px;
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}
.section-title {
  font-size: 16px;
  font-weight: bold;
  color: var(--el-color-primary);
}

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

.model-response {
  white-space: pre-wrap;
  line-height: 1.8;
  color: var(--text-primary);
}
.model-response ol {
    padding-left: 20px;
}
.model-response li {
    margin-bottom: 10px;
}
/* 【新增占位符样式】 */
.content-placeholder {
    padding: 20px;
    text-align: center;
    color: var(--text-secondary);
}


/* --- 评分区域 --- */
.rating-card {
  margin-top: 20px;
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}
.rating-title {
    color: var(--el-color-danger);
}
.el-form-item {
    margin-bottom: 15px;
}

.comprehensive-score-item {
    display: flex;
    justify-content: center;
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
    padding:0;
    font-size: 16px;
    font-weight: bold;
    border-radius: 50% !important;
    border: 2px solid var(--border-color);
    background-color: var(--bg-tertiary);
    color: var(--text-primary);
    transition: all 0.2s ease;
}

.round-rating-group :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
    background-color: var(--el-color-primary) !important;
    color: #ffffff !important;
    border-color: var(--el-color-primary) !important;
    transform: scale(1.05);
}

.round-rating-group :deep(.el-radio-button__inner:hover) {
    color: var(--el-color-primary);
    border-color: var(--el-color-primary-light-3);
    cursor: pointer;
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
  width: 100%;
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
/* --- 底部导航 --- */
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

.item-list-btn-wrapper {
    width: auto;
    margin: 0 10px;
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

/* --- 抽屉样式 --- */
.item-id-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    padding: 20px 10px;
    border-bottom: 1px solid var(--border-color);
}

.item-id-button {
    height: 40px;
    font-size: 14px;
    font-weight: bold;
    border-radius: 4px; 
}

.item-id-button.is-current {
    border: 2px solid var(--el-color-success); 
    box-shadow: 0 0 5px rgba(103, 194, 58, 0.5);
    background-color: var(--el-color-success-light-9);
    color: var(--el-color-success);
}

.drawer-legend {
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    font-size: 14px;
}
.current-tag {
    background-color: transparent !important;
    border: 1px solid var(--el-color-success);
    color: var(--el-color-success);
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
.gen-image-container {
  margin-top: 15px;
  width: 100%;
}
.responsive-gen-image {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}
</style>