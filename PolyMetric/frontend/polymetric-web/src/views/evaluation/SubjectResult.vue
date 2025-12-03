<template>
  <div class="evaluation-page">
    <el-card class="eval-card" shadow="never">
      <template #header>
        <div class="card-header">
          <h2 class="title result-title">主观评测结果查看</h2>
          <el-tag type="success">任务 ID: TASK-SUB-001</el-tag>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="input-card" shadow="hover">
            <template #header>
              <span class="section-title">我的评测要求 (Prompt)</span>
            </template>
            <blockquote class="prompt-text">
              我想了解文艺复兴时期的代表人物和主要成就。
            </blockquote>
            <p class="meta-info">数据集：历史知识库 | 类型：开放式问答</p>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="model-output-card" shadow="hover">
            <template #header>
              <span class="section-title">模型输出 (Model Output)</span>
            </template>
            <div class="model-response">
              <p>好的，文艺复兴 (约14世纪至17世纪) 是欧洲历史上一个思想、文化和艺术空前繁荣的时期，...</p>
              <ol>
                <li><strong>列奥纳多·达·芬奇 — “全能天才”</strong><br>艺术成就：...</li>
                <li><strong>米开朗基罗 — “神圣的雕塑家”</strong><br>雕塑成就：...</li>
              </ol>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="rating-card" shadow="always">
        <template #header>
          <span class="section-title result-score-title">已完成评分 (最终结果)</span>
        </template>
        
        <el-form :model="form" >
          
          <el-form-item class ="comprehensive-score-item">
            <div class="score-labels-low">
                <span class="label-low">极差 (1)</span>
            </div>
            <el-radio-group 
              v-model="form.comprehensive_score" 
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
      
      <div class="navigation-footer">
        <el-pagination
          small
          layout="prev, pager, next"
          :total="100"
          :page-size="1"
          :current-page="3"
          :pager-count="11"
          disabled />
        
        <div class="action-buttons">
            <el-button type="info" @click="handleReturn">返回报告列表</el-button>
        </div>
      </div>

    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// --- 评分表单数据 (模拟从后端获取的已提交结果) ---
const form = ref({
  comprehensive_score: 8, // 已经提交的评分
});

const handleReturn = () => {
  router.push({path: `/evaluation`});
};
</script>

<style scoped>
/* ---------------------------------------------------- */
/* **** 样式与评测页保持一致，仅修改标题颜色和字体 **** */
/* ---------------------------------------------------- */
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
/* 突出结果页的标题 */
.result-title {
    color: var(--el-color-success);
}
.result-score-title {
    color: var(--el-color-primary);
}


/* --- 内容区域 (保持不变) --- */
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
/* --- 评分区域 --- */
.rating-card {
  margin-top: 20px;
}
.el-form-item {
    margin-bottom: 15px;
}

.comprehensive-score-item :deep(.el-form-item__content) {
    display: flex;
    justify-content: center; 
    align-items: center; 
    gap: 10px; /* 设置子元素之间有 10px 间隙 */
}

/* --- 评分按钮样式 (与评测页共享) --- */
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
/* 由于设置了 disabled，这里只需要确保禁用状态下的样式正确 */
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
/* 确保选中的样式在禁用状态下依然可见 */
.round-rating-group :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
    background-color: var(--el-color-success) !important; /* 结果页使用 success 色更合适 */
    color: var(--el-color-white) !important;
    border-color: var(--el-color-success) !important;
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
.action-buttons .el-button {
    margin-left: 10px;
}
</style>