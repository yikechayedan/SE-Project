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
            <p class="meta-info">数据集：历史知识库 | 类型：开放式问答</p>
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
          <el-form-item class ="comprehensive-score-item">
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
                <span>条目列表 ({{ totalCount }}</span>)
            </el-button>
        </div>

        <div class="pagination-controls">
            <el-pagination
              small
              layout="prev, pager, next"
              :total="totalCount"
              :page-size="1"
              :current-page="currentPendingIndex + 1"
              :pager-count="11"
              @current-change="handlePageChange"
              class="custom-pager"
            />
            
            <div class="goto-input">
                <el-input-number
                    v-if="totalCount > 0"
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
                v-for="(id, index) in pendingItems"
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
            <el-tag type="primary">已提交 (蓝色)</el-tag>
            <el-tag type="info" plain>待提交 (白色)</el-tag>
            <el-tag type="success" class="current-tag">当前条目 (绿色边框)</el-tag>
        </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Tickets } from '@element-plus/icons-vue' // 【新增导入】


// --- 模拟数据和后端接口 ---
// 【新增模拟数据】
const mockPendingItems = [
    'TASK-ITEM-001', 'TASK-ITEM-002', 'TASK-ITEM-003' 
];

const mockItemDetails = {
    'TASK-ITEM-001': {
        method: "subjective",
        itemID: "TASK-ITEM-001",
        item_content: {
            input_query: "我想了解文艺复兴时期的代表人物和主要成就。",
            myModel1_response: `
              <p>好的，文艺复兴...</p>
              <ol><li><strong>达·芬奇</strong>：《蒙娜丽莎》。</li><li><strong>米开朗基罗</strong>：《大卫》。</li></ol>
            `,
        }
    },
    'TASK-ITEM-002': {
        method: "subjective",
        itemID: "TASK-ITEM-002",
        item_content: {
            input_query: "请用一段话解释量子纠缠。",
            myModel1_response: "量子纠缠就像是一对分手的恋人...",
        }
    },
    'TASK-ITEM-003': {
        method: "subjective",
        itemID: "TASK-ITEM-003",
        item_content: {
            input_query: "什么是黑洞的事件视界？",
            myModel1_response: "事件视界是黑洞周围的一个边界...",
        }
    },
};

const fetchPendingItems = async (taskId, reviewerId) => {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({
                task: taskId,
                reviewer: reviewerId,
                pending_count: 3,
                pengdingItem_ids: mockPendingItems,
            });
        }, 500);
    });
};

const fetchItemDetail = async (taskId, itemId) => {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            const detail = mockItemDetails[itemId];
            if (detail) {
                resolve(detail);
            } else {
                reject(new Error(`Item detail for ID ${itemId} not found.`));
            }
        }, 500);
    });
};

const submitEvaluation = async (payload) => {
    console.log("提交评分数据:", payload);
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({ success: true, message: "评分提交成功" });
        }, 300);
    });
};

// --- Vue 响应式状态 ---

// 【修改点 7：props 结构统一】
const props = defineProps({
    taskId: { type: [String, Number], required: true, default: 'TASK-SUB-001' },
    reviewerId: { type: [String, Number], required: false, default: 1 }
});

const loading = ref(false);
const submitting = ref(false);

const pendingItems = ref([]);
const totalCount = ref(0);
const currentPendingIndex = ref(-1);
const currentItem = reactive({
    itemID: null,
    item_content: null,
});

// 【修改点 8：统一评分字段为 score】
const form = reactive({
    itemID: null,
    score: null, 
});

const gotoPageNum = ref(1);

// 【新增状态】
const drawerVisible = ref(false); 
const submissionStatus = reactive(new Map());
// 【新增核心状态：本地保存评分】
const savedScores = reactive(new Map());


// --- 计算属性 ---

const canGoPrevious = computed(() => currentPendingIndex.value > 0);
const isLastItem = computed(() => currentPendingIndex.value === pendingItems.value.length - 1);
const currentItemId = computed(() => {
    if (currentPendingIndex.value >= 0 && pendingItems.value.length > currentPendingIndex.value) {
        return pendingItems.value[currentPendingIndex.value];
    }
    return null;
});


// --- 核心方法 ---

const initEvaluation = async () => {
    loading.value = true;
    try {
        const response = await fetchPendingItems(props.taskId, props.reviewerId);
        pendingItems.value = response.pengdingItem_ids;
        totalCount.value = response.pending_count;
        
        // 初始化提交状态
        submissionStatus.clear();
        if (pendingItems.value.length > 0) {
            pendingItems.value.forEach(id => {
                submissionStatus.set(id, false);
            });
            currentPendingIndex.value = 0;
        } else {
            ElMessage.warning('当前任务没有待评测条目。');
        }
    } catch (error) {
        ElMessage.error('获取待测列表失败: ' + error.message);
    } finally {
        loading.value = false;
    }
};

// 【修改点 9：加载时检查本地评分并回显】
const loadItemDetail = async (itemId) => {
    if (!itemId) return;

    loading.value = true;
    currentItem.itemID = null; 
    currentItem.item_content = null;

    try {
        const response = await fetchItemDetail(props.taskId, itemId);
        
        currentItem.itemID = response.itemID;
        currentItem.item_content = response.item_content;
        
        form.itemID = response.itemID;
        
        // 检查是否有本地保存的评分
        const savedScore = savedScores.get(response.itemID);
        if (savedScore !== undefined) {
            form.score = savedScore; // 如果有保存值，则回显
        } else {
            form.score = null; // 否则重置为 null 
        }
        
        gotoPageNum.value = currentPendingIndex.value + 1;

    } catch (error) {
        ElMessage.error(`加载条目 ${itemId} 详情失败: ` + error.message);
    } finally {
        loading.value = false;
    }
};

// 【修改点 10：提交成功后保存评分到本地 Map】
const handleNext = async () => {
    if (form.score === null) {
        ElMessage.warning('请先为当前条目评分 (1-10)。');
        return;
    }

    submitting.value = true;
    const payload = {
        method: "subjective",
        myModel: 1, 
        dataset: 1,
        reviewer: props.reviewerId,
        time_stamp: new Date().toISOString(),
        itemID: form.itemID,
        score: form.score,
    };

    try {
        const result = await submitEvaluation(payload);

        if (result.success) {
            ElMessage.success(`条目 ${form.itemID} 评分提交成功!`);
            
            // 更新提交状态和本地保存的评分
            submissionStatus.set(form.itemID, true);
            savedScores.set(form.itemID, form.score);
            
            if (!isLastItem.value) {
                currentPendingIndex.value += 1;
            } else {
                ElMessage.info('所有待测条目已完成评测！');
            }
        } else {
            ElMessage.error('评分提交失败，请重试。');
        }
    } catch (error) {
        ElMessage.error('提交评分时发生错误: ' + error.message);
    } finally {
        submitting.value = false;
    }
};

const handlePrevious = () => {
    if (canGoPrevious.value) {
        currentPendingIndex.value -= 1;
    } else {
        ElMessage.info('当前已是第一题。');
    }
};

const handlePageChange = (page) => {
    currentPendingIndex.value = page - 1;
};

// 【修改点 11：跳转逻辑】
const handleGotoPage = (value) => {
    const totalPages = pendingItems.value.length;
    
    if (value === null || value < 1 || value > totalPages) {
        ElMessage.warning(`不存在该页面，请输入 1 到 ${totalPages} 之间的页码。`);
        setTimeout(() => {
            gotoPageNum.value = currentPendingIndex.value + 1;
        }, 50); 
        return;
    }
    
    currentPendingIndex.value = value - 1;
};

// 【修改点 12：通过 ID 跳转逻辑】
const handleJumpToItemById = (itemId) => {
    const index = pendingItems.value.findIndex(id => id === itemId);
    if (index !== -1 && index !== currentPendingIndex.value) {
        currentPendingIndex.value = index;
    }
    drawerVisible.value = false;
};


// --- 生命周期和监听器 ---

onMounted(() => {
    initEvaluation();
});

watch(currentPendingIndex, (newIndex) => {
    if (newIndex >= 0 && newIndex < pendingItems.value.length) {
        const itemId = pendingItems.value[newIndex];
        loadItemDetail(itemId);
    }
}, { immediate: false }); 
</script>

<style scoped>
/* 保持原有样式不变 */
.evaluation-page {
  padding: 20px;
  background-color: #f0f2f5;
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
  color: #303133;
}

/* --- 内容区域 --- */
.input-card, .model-output-card {
  height: 400px; 
  overflow-y: auto; 
  margin-bottom: 20px;
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
  background-color: var(--el-color-info-light-9);
  color: #606266;
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
  color: #303133;
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
    color: #909399;
}


/* --- 评分区域 --- */
.rating-card {
  margin-top: 20px;
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
    border: 2px solid var(--el-color-info-light-7);
    background-color: var(--el-color-white);
    transition: all 0.2s ease;
}

.round-rating-group :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
    background-color: var(--el-color-primary) !important;
    color: var(--el-color-white) !important;
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
  border-top: 1px solid #ebeef5;
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
}

/* --- 抽屉样式 --- */
.item-id-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    padding: 20px 10px;
    border-bottom: 1px solid #ebeef5;
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