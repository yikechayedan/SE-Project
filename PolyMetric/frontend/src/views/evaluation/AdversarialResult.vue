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
            <el-tag type="warning" size="large">任务 ID: {{ reportData.id }}</el-tag>
          </div>
        </template>

        <el-row :gutter="20" class="meta-row">
          <el-col :span="12">
            <el-card shadow="hover" class="meta-item-card">
              <div class="meta-label">任务状态</div>
              <div class="meta-value status">
                <el-tag :type="reportData.status === 'completed' ? 'success' : 'info'" effect="dark">
                  {{ reportData.status }}
                </el-tag>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover" class="meta-item-card">
              <div class="meta-label">评测方法</div>
              <div class="meta-value info">双模型对抗 (Pairwise)</div>
            </el-card>
          </el-col>
        </el-row>

        <el-divider />

        <div v-if="currentItem">
          <el-card class="prompt-card" shadow="hover">
            <template #header>
              <span class="section-title prompt-title">问题 (Question) - 条目 ID: {{ currentItem.id }}</span>
            </template>
            <blockquote class="prompt-text">
              {{ currentItem.content }}
            </blockquote>
          </el-card>

          <el-row :gutter="20" class="model-comparison">
            <el-col :span="12">
              <el-card class="model-output-card" shadow="hover">
                <template #header>
                  <span class="section-title model-a-title">左侧：模型 A 输出</span>
                </template>
                <div class="model-response">
                  {{ currentItem.predicted_answer }}
                </div>
              </el-card>
            </el-col>

            <el-col :span="12">
              <el-card class="model-output-card" shadow="hover">
                <template #header>
                  <span class="section-title model-b-title">右侧：模型 B 输出</span>
                </template>
                <div class="model-response">
                  {{ currentItem.predicted_answer_2 }}
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
import { Histogram } from '@element-plus/icons-vue';
import { getEvaluationTaskDetail } from '../../api/tasks.js';
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

const reportData = ref({
  id: null,
  status: '',
  data: [] // 后端响应体包含 predicted_answer, predicted_answer2, preference
});

// 计算属性
const totalCount = computed(() => reportData.value.data?.length || 0);

const currentItem = computed(() => {
  if (totalCount.value === 0) return null;
  return reportData.value.data[currentPage.value - 1];
});

// 数据获取
const fetchReportData = async () => {
  loading.value = true;
  errorMessage.value = null;
  try {
    const response = await getEvaluationTaskDetail(props.taskId);
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
  background-color: #f7f9fc;
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
  color: #2c3e50;
  margin: 0;
}

/* 基础信息卡片样式 */
.meta-row {
  margin-bottom: 20px;
}
.meta-item-card {
  text-align: center;
  border-radius: 10px;
}
.meta-label {
  font-size: 14px;
  color: #8c939d;
  margin-bottom: 8px;
}
.meta-value {
  font-size: 20px;
  font-weight: bold;
}

/* 问题区域 */
.section-title {
  font-size: 18px;
  font-weight: 600;
}
.prompt-card {
  margin-bottom: 20px;
}
.prompt-text {
  padding: 15px;
  border-left: 5px solid #409eff;
  background-color: #f0f7ff;
  color: #444;
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
}
.model-a-title { color: #67c23a; }
.model-b-title { color: #e6a23c; }
.model-response {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #333;
}

/* 评分/偏好展示 */
.rating-card {
  text-align: center;
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

/* 底部导航 */
.navigation-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
.page-navigation {
  width: 150px;
}
.pagination-controls {
  display: flex;
  align-items: center;
}
</style>