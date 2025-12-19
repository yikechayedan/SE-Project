<template>
  <div class="evaluation-page">
    <el-card class="eval-card" shadow="never" v-loading="loading"> 
      <template #header>
        <div class="card-header">
          <h2 class="title">对抗评测</h2>
          <el-tag type="warning">任务 ID: {{ taskId }}</el-tag>
        </div>
      </template>

      <el-card class="prompt-card" shadow="hover">
          <template #header>
            <span class="section-title prompt-title">问题 (Question)</span>
          </template>
          <blockquote class="prompt-text" v-if="currentItem.itemID">
            {{ currentItem.item_content.input_query }}
          </blockquote>
          <div v-else class="content-placeholder">请等待问题加载...</div>
          <p class="meta-info">数据集 ID：{{ datasetId }} | 类型：开放式问答</p>
      </el-card>

      <el-row :gutter="20" class="model-comparison">
        <el-col :span="12">
          <el-card class="model-output-card" shadow="hover">
            <template #header>
              <span class="section-title model-a-title">左侧：模型 A (V1.0)</span>
            </template>
            <div class="model-response" v-if="currentItem.itemID" v-html="currentItem.item_content.myModel1_response"></div>
            <div v-else class="content-placeholder">请等待模型 A 输出加载...</div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="model-output-card" shadow="hover">
            <template #header>
              <span class="section-title model-b-title">右侧：模型 B (V2.0)</span>
            </template>
            <div class="model-response" v-if="currentItem.itemID" v-html="currentItem.item_content.myModel2_response"></div>
            <div v-else class="content-placeholder">请等待模型 B 输出加载...</div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="rating-card" shadow="always">
        <template #header>
          <span class="section-title judgement-title">请判断哪个模型回答更好</span>
        </template>
        
        <el-form :model="form" v-if="currentItem.itemID" class="preference-form">
          <el-form-item>
            <el-radio-group v-model="form.preference" size="large" class="custom-radio-group">
              <el-radio-button label="left">左边更好</el-radio-button>
              <el-radio-button label="tie">平局 / 差不多</el-radio-button>
              <el-radio-button label="right">右边更好</el-radio-button>
            </el-radio-group>
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
                :disabled="form.preference === null || loading"
            >
                {{ isLastItem ? '提交完成' : '提交并下一题' }}
            </el-button>
        </div>
      </div>

    </el-card>
    
    <el-drawer v-model="drawerVisible" title="评测条目列表" direction="rtl" size="350px">
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
            <el-tag type="primary">已提交 (蓝色)</el-tag>
            <el-tag type="info" plain>待提交 (白色)</el-tag>
            <el-tag type="success" class="current-tag">当前条目 (绿色边框)</el-tag>
        </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter } from 'vue-router';
import { Tickets } from '@element-plus/icons-vue';
import { getPendingItems, getItemDetail, submitSubjectiveScore } from '@/api/tasks.js';

const props = defineProps({
    taskId: { type: [String, Number], required: true},
    reviewerId: { type: [String, Number], required: true},
    modelId: { type: [String, Number], required: true },
    model2Id: { type: [String, Number], required: true },
    datasetId: { type: [String, Number], required: true }
});

const router = useRouter();
const loading = ref(false);
const submitting = ref(false);
const drawerVisible = ref(false);

const totalCount = ref(0);
const allItemIds = ref([]);
const pendingItemIds = ref([]);
const submissionStatus = ref(new Map());

const currentItemId = ref(null);
const currentItem = ref({ itemID: null, item_content: { input_query: '', myModel1_response: '', myModel2_response: '' } });

const form = reactive({ preference: null });
const gotoPageNum = ref(1);

// --- 计算属性 ---
const currentPageIndex = computed(() => {
  if (!allItemIds.value.length) return 1;
  const index = allItemIds.value.indexOf(currentItemId.value);
  return index !== -1 ? index + 1 : 1;
});

const canGoPrevious = computed(() => currentPageIndex.value > 1);

const isLastItem = computed(() => {
  if (!pendingItemIds.value.length) return false;
  return pendingItemIds.value.length === 1 && pendingItemIds.value.includes(currentItemId.value);
});

// --- 核心方法 ---

const initData = async () => {
    loading.value = true;
    try {
        const res = await getPendingItems(props.taskId, props.reviewerId);
        allItemIds.value = res.data.all_item_ids || [];
        pendingItemIds.value = res.data.pengding_item_ids || []; // 注意这里接口字段拼写与主观评测保持一致
        totalCount.value = res.data.total_count || 0;

        const pendingSet = new Set(pendingItemIds.value);
        allItemIds.value.forEach(id => {
            submissionStatus.value.set(id, !pendingSet.has(id));
        });

        const targetId = pendingItemIds.value.length > 0 ? pendingItemIds.value[0] : allItemIds.value[0];
        if (targetId) await fetchDetail(targetId);
    } catch (error) {
        ElMessage.error('初始化数据失败');
    } finally {
        loading.value = false;
    }
};

const fetchDetail = async (id) => {
    loading.value = true;
    currentItemId.value = id;
    try {
        const res = await getItemDetail(props.taskId, id);
        currentItem.value = res.data;
        form.preference = null; // 切换题目重置
        gotoPageNum.value = currentPageIndex.value;
    } catch (error) {
        ElMessage.error('加载详情失败');
    } finally {
        loading.value = false;
    }
};

const handleSubmit = async () => {
    if (isLastItem.value) {
        ElMessageBox.confirm('这是最后一题，提交后将结束评测。', '提示', {
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
            method: "adversarial",
            reviewer: props.reviewerId,
            myModel: props.modelId,
            myModel2: props.model2Id, // 对抗评测特有
            dataset: props.datasetId,
            itemID: currentItemId.value,
            preference: form.preference,
            score: null // 对抗评测下 score 默认为 null
        };

        await submitSubjectiveScore(props.taskId, payload);
        ElMessage.success('提交成功');

        submissionStatus.value.set(currentItemId.value, true);

        const res = await getPendingItems(props.taskId, props.reviewerId);
        pendingItemIds.value = res.data.pengding_item_ids;

        if (isFinal) {
            router.push({ name: 'Evaluation' });
        } else {
            const nextPendingId = pendingItemIds.value.find(id => id !== currentItemId.value) || pendingItemIds.value[0];
            if (nextPendingId) fetchDetail(nextPendingId);
        }
    } catch (error) {
        ElMessage.error('提交失败');
    } finally {
        submitting.value = false;
    }
};

// --- 交互方法 ---
const handlePrevious = () => {
    const index = allItemIds.value.indexOf(currentItemId.value);
    if (index > 0) fetchDetail(allItemIds.value[index - 1]);
};

const handlePageChange = (page) => {
    if (allItemIds.value[page - 1]) fetchDetail(allItemIds.value[page - 1]);
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

/* --- Prompt 区域 --- */
.prompt-card {
    margin-bottom: 20px;
    background-color: var(--bg-secondary);
    border-color: var(--border-color);
}
.prompt-title {
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

/* --- 模型输出比较区域 --- */
.model-comparison {
    margin-bottom: 20px;
}
.model-output-card {
  height: 450px; 
  overflow-y: auto; 
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}

.model-a-title {
    color: var(--el-color-success);
}
.model-b-title {
    color: var(--el-color-warning);
}

.model-response {
  line-height: 1.6;
  color: var(--text-primary);
}
.model-response ol {
    padding-left: 20px;
}
.content-placeholder {
    padding: 20px;
    text-align: center;
    color: var(--text-secondary);
}

/* --- 评判区域 --- */
.rating-card {
  margin-top: 5px;
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
}
.judgement-title {
    color: var(--el-color-danger); 
}
.el-form-item {
    margin-bottom: 15px;
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