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
          <p class="meta-info">数据集：历史知识库 | 类型：开放式问答</p>
      </el-card>


      <el-row :gutter="20" class="model-comparison">
        
        <el-col :span="12">
          <el-card class="model-output-card" shadow="hover">
            <template #header>
              <span class="section-title model-a-title">左侧：模型 A (V1.0)</span>
            </template>
            <div class="model-response" v-if="currentItem.itemID" v-html="currentItem.item_content.modelA_response">
            </div>
            <div v-else class="content-placeholder">请等待模型 A 输出加载...</div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="model-output-card" shadow="hover">
            <template #header>
              <span class="section-title model-b-title">右侧：模型 B (V2.0 - 待优化)</span>
            </template>
            <div class="model-response" v-if="currentItem.itemID" v-html="currentItem.item_content.modelB_response">
            </div>
            <div v-else class="content-placeholder">请等待模型 B 输出加载...</div>
          </el-card>
        </el-col>
      </el-row>


      <el-card class="rating-card" shadow="always">
        <template #header>
          <span class="section-title judgement-title">请判断哪个模型回答更好</span>
        </template>
        
        <el-form :model="form" label-width="150px" label-position="left" v-if="currentItem.itemID">
          
          <el-form-item label="综合倾向性判断">
            <el-radio-group v-model="form.preference" size="large">
              <el-radio-button label="左边更好" value="left" />
              <el-radio-button label="平局" value="tie" />
              <el-radio-button label="右边更好" value="right" />
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
                条目列表 ({{ pendingItems.length }})
            </el-button>
        </div>

        <div class="pagination-controls">
            <el-pagination
              small
              layout="prev, pager, next"
              :total="pendingItems.length"
              :page-size="1"
              :current-page="currentPendingIndex + 1"
              :pager-count="11"
              @current-change="handlePageChange"
              class="custom-pager"
            />
            
            <div class="goto-input">
                <el-input-number
                    v-if="pendingItems.length > 0"
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
                :disabled="form.preference === null || loading"
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
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { Tickets } from '@element-plus/icons-vue' 


// --- 模拟数据和后端接口 (保持不变) ---
const mockPendingItems = ['ADV-001', 'ADV-002', 'ADV-003'];

const mockItemDetails = {
    'ADV-001': {
        method: "adversarial",
        itemID: "ADV-001",
        item_content: {
            input_query: "我想了解文艺复兴时期的代表人物和主要成就。",
            modelA_response: `<p>好的，文艺复兴 (约14世纪至17世纪) 是欧洲历史上一个思想、文化和艺术空前繁荣的时期，也被称为"黑暗的中世纪"之后的重生。其核心精神是人文主义，即关注人本身、现实世界和古典文化，而非以中世纪那样一切以神为中心。</p><ol><li>**达芬奇**：代表作《蒙娜丽莎》。他在解剖学、工程设计、光学等领域也有重要贡献，是文艺复兴的代表人物。</li><li>**米开朗基罗**：创作了著名的雕塑《大卫》和《哀悼基督》，以及西斯廷教堂的宏伟壁画《创世纪》，是雕塑史上的巅峰。</li></ol>`,
            modelB_response: `<p>文艺复兴的核心在于 **人文主义**。它的开始标志是但丁的《神曲》。</p><p>以下是这一时期最杰出的代表人物及其主要成就：</p><ol><li>**莱昂纳多·达·芬奇**：创作了《蒙娜丽莎》，但其价值主要在于他设计的各种机械和飞行器。</li><li>**拉斐尔**：代表作《雅典学院》。他以和谐和典雅著称，与达芬奇和米开朗基罗并称“文艺复兴三杰”。</li></ol>`,
        }
    },
    'ADV-002': { method: "adversarial", itemID: "ADV-002", item_content: { input_query: "解释什么是量子纠缠？", modelA_response: "模型A的量子纠缠解释...", modelB_response: "模型B的量子纠缠解释..." } },
    'ADV-003': { method: "adversarial", itemID: "ADV-003", item_content: { input_query: "什么是黑洞事件视界？", modelA_response: "模型A的黑洞解释...", modelB_response: "模型B的黑洞解释..." } },
};

const fetchPendingItems = async (taskId, reviewerId) => {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({
                task: taskId,
                reviewer: reviewerId,
                pending_count: mockPendingItems.length,
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

const props = defineProps({
    taskId: { type: [String, Number], required: true, default: 'TASK-ADV-001' },
    reviewerId: { type: [String, Number], required: false, default: 1 }
});

const loading = ref(false);
const submitting = ref(false);

const pendingItems = ref([]);
const currentPendingIndex = ref(-1);
const currentItem = reactive({ itemID: null, item_content: null });

const form = reactive({
    itemID: null,
    preference: null,
});

const gotoPageNum = ref(1);

const drawerVisible = ref(false); 
const submissionStatus = reactive(new Map());

// 【新增点 1：本地保存评分值的 Map】
const savedPreferences = reactive(new Map());


// --- 计算属性 (保持不变) ---
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

// 【修改点 2：在加载时检查本地评分并回显】
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
        const savedPref = savedPreferences.get(response.itemID);
        if (savedPref) {
            form.preference = savedPref; // 如果有保存值，则显示它
        } else {
            form.preference = null; // 否则重置为 null (要求用户必须评分)
        }
        
        gotoPageNum.value = currentPendingIndex.value + 1;

    } catch (error) {
        ElMessage.error(`加载条目 ${itemId} 详情失败: ` + error.message);
    } finally {
        loading.value = false;
    }
};

// 【修改点 3：在提交成功后保存评分到本地 Map】
const handleNext = async () => {
    if (form.preference === null) {
        ElMessage.warning('请先选择一个评测倾向。');
        return;
    }

    submitting.value = true;
    const payload = {
        method: "adversarial",
        reviewer: props.reviewerId,
        time_stamp: new Date().toISOString(),
        itemID: form.itemID,
        preference: form.preference,
    };

    try {
        const result = await submitEvaluation(payload);

        if (result.success) {
            ElMessage.success(`条目 ${form.itemID} 评测提交成功!`);
            
            submissionStatus.set(form.itemID, true);
            // 保存当前的评分到本地 Map
            savedPreferences.set(form.itemID, form.preference);
            
            if (!isLastItem.value) {
                currentPendingIndex.value += 1;
            } else {
                ElMessage.info('所有待测条目已完成评测！');
            }
        } else {
            ElMessage.error('评测提交失败，请重试。');
        }
    } catch (error) {
        ElMessage.error('提交评测时发生错误: ' + error.message);
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

const handleJumpToItemById = (itemId) => {
    const index = pendingItems.value.findIndex(id => id === itemId);
    if (index !== -1 && index !== currentPendingIndex.value) {
        currentPendingIndex.value = index;
    }
    drawerVisible.value = false;
};


// --- 生命周期和监听器 (保持不变) ---

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
/* ... */
.prompt-text {
  padding: 10px;
  border-left: 5px solid var(--el-color-info-light-5);
  margin: 10px 0;
  background-color: var(--el-color-info-light-9);
  color: var(--text-primary);
  font-style: italic;
  min-height: 100px;
}
/* ... */
.model-response {
  line-height: 1.6;
  color: var(--text-primary);
}
.content-placeholder {
    padding: 20px;
    text-align: center;
    color: var(--text-secondary);
}
/* --- 评判区域 --- */
.rating-card {
  margin-top: 5px;
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