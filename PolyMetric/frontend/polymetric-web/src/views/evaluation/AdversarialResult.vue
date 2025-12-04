<template>
  <div class="evaluation-page">
    <el-card class="eval-card" shadow="never">
      <template #header>
        <div class="card-header">
          <h2 class="title">对抗评测结果查看</h2>
          <el-tag type="warning">任务 ID: TASK-ADV-002</el-tag>
        </div>
      </template>

      <el-card class="prompt-card" shadow="hover">
          <template #header>
            <span class="section-title prompt-title">问题 (Question)</span>
          </template>
          <blockquote class="prompt-text">
            我想了解文艺复兴时期的代表人物和主要成就。
          </blockquote>
          <p class="meta-info">数据集：历史知识库 | 类型：开放式问答</p>
      </el-card>


      <el-row :gutter="20" class="model-comparison">
        
        <el-col :span="12">
          <el-card class="model-output-card" shadow="hover">
            <template #header>
              <span class="section-title model-a-title">左侧：模型 A (V1.0)</span>
            </template>
            <div class="model-response">
              <p>好的，文艺复兴 (约14世纪至17世纪) 是欧洲历史上一个思想、文化和艺术空前繁荣的时期，也被称为"黑暗的中世纪"之后的重生。其核心精神是人文主义，即关注人本身、现实世界和古典文化，而非以中世纪那样一切以神为中心。</p>
              <ol>
                <li>**达芬奇**：代表作《蒙娜丽莎》。他在解剖学、工程设计、光学等领域也有重要贡献，是文艺复兴的代表人物。</li>
                <li>**米开朗基罗**：创作了著名的雕塑《大卫》和《哀悼基督》，以及西斯廷教堂的宏伟壁画《创世纪》，是雕塑史上的巅峰。</li>
              </ol>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="model-output-card" shadow="hover">
            <template #header>
              <span class="section-title model-b-title">右侧：模型 B (V2.0 - 待优化)</span>
            </template>
            <div class="model-response">
              <p>文艺复兴的核心在于 **人文主义**。它的开始标志是但丁的《神曲》。</p>
              <p>以下是这一时期最杰出的代表人物及其主要成就：</p>
              <ol>
                <li>**莱昂纳多·达·芬奇**：创作了《蒙娜丽莎》，但其价值主要在于他设计的各种机械和飞行器。</li>
                <li>**拉斐尔**：代表作《雅典学院》。他以和谐和典雅著称，与达芬奇和米开朗基罗并称“文艺复兴三杰”。</li>
              </ol>
            </div>
          </el-card>
        </el-col>
      </el-row>


      <el-card class="rating-card" shadow="always">
        <template #header>
          <span class="section-title judgement-title">请判断哪个模型回答更好</span>
        </template>
        
        <el-form :model="form" label-width="150px" label-position="left">
          
          <el-form-item label="综合倾向性判断">
            <el-radio-group
             v-model="form.preference"
             size="large"
             disabled>
              <el-radio-button label="左边更好" value="left" />
              <el-radio-button label="平局" value="both" />
              <el-radio-button label="右边更好" value="right" />
              <el-radio-button label="两边均差" value="neither" />
            </el-radio-group>
          </el-form-item>

        </el-form>
      </el-card>
      
      <div class="navigation-footer">
    
        <el-pagination
          small
          layout="prev, pager, next"
          :total="100"
          :page-size="1"
          :current-page="12"
          :pager-count="11"
          disabled
        />
        
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

const props = defineProps({
    taskId: {
        type: String, // ID 可能是字符串或数字
        required: true
    }
});

const router = useRouter();

// --- 表单数据 ---
const form = ref({
  preference: 'left', // 默认选中左边
});

// --- 操作函数 (静态演示) ---
const handleReturn = () => {
  router.push({path: `/evaluation`});
};
</script>

<style scoped>
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
  color: var(--el-color-success);
}

/* --- Prompt 区域 --- */
.prompt-card {
    margin-bottom: 20px;
}
.prompt-title {
    color: var(--el-color-primary);
}
.prompt-text {
  padding: 10px;
  border-left: 5px solid var(--el-color-info-light-5);
  margin: 10px 0;
  background-color: var(--el-color-info-light-9);
  color: #606266;
  font-style: italic;
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
  height: 450px; /* 固定高度，保持左右对齐 */
  overflow-y: auto; /* 允许滚动 */
}

/* 强调左右侧模型名称 */
.model-a-title {
    color: var(--el-color-success);
}
.model-b-title {
    color: var(--el-color-warning);
}

.model-response {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #303133;
}
.model-response ol {
    padding-left: 20px;
}
.summary-note {
    margin-top: 15px;
    padding: 10px;
    background-color: var(--el-color-info-light-9);
    border-left: 3px solid var(--el-color-info-light-5);
    font-size: 14px;
}

/* --- 评判区域 --- */
.rating-card {
  margin-top: 5px;
}
.judgement-title {
    color: var(--el-color-danger); /* 强调需要用户操作 */
}
.el-form-item :deep(.el-radio-button__inner) {
    /* 确保在禁用状态下也能正确应用颜色 */
    transition: all 0.2s ease;
    /* 统一默认边框，防止禁用时边框颜色差异过大 */
    border-color: var(--el-border-color-light) !important;
}

/* 选中状态的样式覆盖（使用 Success 绿色） */
.el-form-item :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
    background-color: var(--el-color-success) !important;
    color: var(--el-color-white) !important;
    border-color: var(--el-color-success) !important;
    
    /* 确保禁用状态下的透明度不会让颜色显得太淡 */
    opacity: 1 !important; 
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
    width: 120px; /* 保证左右按钮区域平衡 */
    text-align: center;
}
</style>