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
            <p class="meta-info">数据集 ID：{{ datasetId }} | 类型：开放式问答</p>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="model-output-card" shadow="hover">
            <template #header>
              <span class="section-title">模型输出 (Model Output)</span>
            </template>
            <div class="model-response" v-if="currentItem.itemID" v-html="currentItem.item_content.myModel1_response">
            </div>
            <div v-else class="content-placeholder">请等待模型输出加载...</div>
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
import { Tickets } from '@element-plus/icons-vue';
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
    currentItem.value = res.data;

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
</style>