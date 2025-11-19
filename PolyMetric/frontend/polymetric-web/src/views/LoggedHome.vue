<template>
  <div class="logged-home">
    <el-card class="banner-card" shadow="always">
      <h2>当前排行榜</h2>
      <div class="actions">
        <el-button type="success" round @click="showEvalDialog = true">开始评测</el-button>
        <el-button type="info" round @click="showTutorial = true">使用教程</el-button>
      </div>
      <el-select v-model="selectedDataset" placeholder="选择数据集" style="margin-bottom: 20px;">
        <el-option label="默认数据集" value="default" />
        <el-option label="数学数据集" value="math" />
        <el-option label="视觉数据集" value="vision" />
      </el-select>
      <el-table :data="rankings" border style="width: 100%;">
        <el-table-column prop="modelName" label="模型名称" />
        <el-table-column prop="objectiveScore" label="客观题得分" />
        <el-table-column prop="subjectiveScore" label="主观题得分" />
        <el-table-column prop="adversarialScore" label="对抗评测得分" />
      </el-table>
    </el-card>

    <!-- 使用教程弹窗 -->
    <el-dialog v-model="showTutorial" title="使用教程" :draggable="true" width="600px">
      <div class="tutorial-content">
        <p>1. 登录账号后，选择左侧菜单进入相应页面。</p>
        <p>2. 在首页点击开始评测，选择数据集和方式提交。</p>
        <p>3. 查看排行榜可切换数据集。</p>
        <p>4. 个人主页管理关注、数据集和任务。</p>
        <p>5. 评测页面查看所有任务，支持搜索和分页。</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="showTutorial = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 评测弹窗 -->
    <EvalDialog v-model:showDialog="showEvalDialog" @close="showEvalDialog = false" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import EvalDialog from '../components/common/EvalDialog.vue'

const selectedDataset = ref('default')
const rankings = ref([
  { modelName: 'Name1', objectiveScore: '10.00', subjectiveScore: '10.00', adversarialScore: '10.00' },
  { modelName: 'Name2', objectiveScore: '9.50', subjectiveScore: '9.80', adversarialScore: '9.70' },
])

watch(selectedDataset, () => ElMessage.success('排行榜已切换数据集'))

const showTutorial = ref(false)
const showEvalDialog = ref(false)
</script>

<style scoped>
.logged-home { padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); height: 100%; }
.banner-card { background: #f5f7fa; color: #333; padding: 20px; border-radius: 12px; }
.actions { margin-bottom: 20px; display: flex; gap: 10px; }
.tutorial-content { line-height: 1.6; color: #666; }
</style>